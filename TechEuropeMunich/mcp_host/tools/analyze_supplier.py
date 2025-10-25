"""
Analyze Supplier Data Tool

This module provides functionality to analyze supplier data from CSV and PDF files,
extracting key information for negotiation training.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import fitz  # PyMuPDF
import re
from datetime import datetime

logger = logging.getLogger(__name__)

async def analyze_supplier_tool(file_path: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze supplier data from CSV or PDF files.
    
    Args:
        file_path: Path to the supplier data file
        session_context: Session context to store extracted data
        
    Returns:
        Dictionary containing extracted supplier information
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.csv':
            supplier_data = await _analyze_csv_file(file_path)
        elif file_extension == '.pdf':
            supplier_data = await _analyze_pdf_file(file_path)
        elif file_extension == '.txt':
            supplier_data = await _analyze_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Store in session context
        session_context['supplier_data'] = supplier_data
        session_context['last_analyzed_file'] = file_path
        session_context['analysis_timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Successfully analyzed supplier data from {file_path}")
        return supplier_data
        
    except Exception as e:
        logger.error(f"Error analyzing supplier file {file_path}: {str(e)}")
        raise

async def _analyze_csv_file(file_path: str) -> Dict[str, Any]:
    """Analyze CSV file for supplier data"""
    try:
        df = pd.read_csv(file_path)
        
        # Extract supplier information
        supplier_data = {
            "file_type": "csv",
            "file_path": file_path,
            "total_rows": len(df),
            "columns": df.columns.tolist(),
            "supplier_name": None,
            "supplier_id": None,
            "products": [],
            "prices": [],
            "delivery_times": [],
            "quality_metrics": [],
            "past_volumes": [],
            "contract_terms": {},
            "raw_data": df.to_dict('records')[:10]  # First 10 rows for context
        }
        
        # Try to identify supplier name and ID
        supplier_data.update(_extract_supplier_identifiers(df))
        
        # Extract product and pricing information
        supplier_data.update(_extract_product_data(df))
        
        # Extract delivery and quality metrics
        supplier_data.update(_extract_metrics(df))
        
        return supplier_data
        
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        raise

async def _analyze_pdf_file(file_path: str) -> Dict[str, Any]:
    """Analyze PDF file for supplier data"""
    try:
        doc = fitz.open(file_path)
        text_content = ""
        
        # Extract text from all pages
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_content += page.get_text()
        
        doc.close()
        
        # Extract supplier information from text
        supplier_data = {
            "file_type": "pdf",
            "file_path": file_path,
            "total_pages": doc.page_count,
            "text_length": len(text_content),
            "supplier_name": None,
            "supplier_id": None,
            "products": [],
            "prices": [],
            "delivery_times": [],
            "quality_metrics": [],
            "past_volumes": [],
            "contract_terms": {},
            "extracted_text": text_content[:2000]  # First 2000 chars for context
        }
        
        # Extract information using regex patterns
        supplier_data.update(_extract_from_text(text_content))
        
        return supplier_data
        
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {str(e)}")
        raise

async def _analyze_text_file(file_path: str) -> Dict[str, Any]:
    """Analyze text file for supplier data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Extract supplier information from text
        supplier_data = {
            "file_type": "text",
            "file_path": file_path,
            "text_length": len(text_content),
            "supplier_name": None,
            "supplier_id": None,
            "products": [],
            "prices": [],
            "delivery_times": [],
            "quality_metrics": [],
            "past_volumes": [],
            "contract_terms": {},
            "extracted_text": text_content[:2000]  # First 2000 chars for context
        }
        
        # Extract information using regex patterns
        supplier_data.update(_extract_from_text(text_content))
        
        return supplier_data
        
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {str(e)}")
        raise

def _extract_supplier_identifiers(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract supplier name and ID from DataFrame"""
    identifiers = {"supplier_name": None, "supplier_id": None}
    
    # Look for common supplier identifier columns
    name_columns = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['supplier', 'vendor', 'company', 'name'])]
    id_columns = [col for col in df.columns if any(keyword in col.lower() 
                  for keyword in ['id', 'code', 'number', 'supplier_id'])]
    
    if name_columns:
        # Get the first non-null value from name columns
        for col in name_columns:
            non_null_values = df[col].dropna()
            if not non_null_values.empty:
                identifiers["supplier_name"] = str(non_null_values.iloc[0])
                break
    
    if id_columns:
        # Get the first non-null value from ID columns
        for col in id_columns:
            non_null_values = df[col].dropna()
            if not non_null_values.empty:
                identifiers["supplier_id"] = str(non_null_values.iloc[0])
                break
    
    return identifiers

def _extract_product_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract product and pricing information from DataFrame"""
    product_data = {"products": [], "prices": []}
    
    # Look for product-related columns
    product_columns = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['product', 'item', 'sku', 'part', 'description'])]
    price_columns = [col for col in df.columns if any(keyword in col.lower() 
                     for keyword in ['price', 'cost', 'rate', 'amount', 'value'])]
    
    # Extract products
    if product_columns:
        for col in product_columns:
            products = df[col].dropna().unique().tolist()
            product_data["products"].extend([str(p) for p in products[:10]])  # Limit to 10
    
    # Extract prices
    if price_columns:
        for col in price_columns:
            prices = df[col].dropna()
            numeric_prices = pd.to_numeric(prices, errors='coerce').dropna()
            if not numeric_prices.empty:
                product_data["prices"].extend(numeric_prices.tolist()[:10])  # Limit to 10
    
    return product_data

def _extract_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract delivery times and quality metrics from DataFrame"""
    metrics = {"delivery_times": [], "quality_metrics": [], "past_volumes": []}
    
    # Look for delivery-related columns
    delivery_columns = [col for col in df.columns if any(keyword in col.lower() 
                        for keyword in ['delivery', 'lead', 'time', 'days', 'duration'])]
    
    # Look for quality-related columns
    quality_columns = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in ['quality', 'rating', 'score', 'defect', 'reject'])]
    
    # Look for volume-related columns
    volume_columns = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['volume', 'quantity', 'amount', 'units', 'qty'])]
    
    # Extract delivery times
    if delivery_columns:
        for col in delivery_columns:
            times = pd.to_numeric(df[col], errors='coerce').dropna()
            if not times.empty:
                metrics["delivery_times"].extend(times.tolist()[:10])
    
    # Extract quality metrics
    if quality_columns:
        for col in quality_columns:
            quality_values = pd.to_numeric(df[col], errors='coerce').dropna()
            if not quality_values.empty:
                metrics["quality_metrics"].extend(quality_values.tolist()[:10])
    
    # Extract volumes
    if volume_columns:
        for col in volume_columns:
            volumes = pd.to_numeric(df[col], errors='coerce').dropna()
            if not volumes.empty:
                metrics["past_volumes"].extend(volumes.tolist()[:10])
    
    return metrics

def _extract_from_text(text: str) -> Dict[str, Any]:
    """Extract supplier information from text using regex patterns"""
    extracted = {
        "supplier_name": None,
        "supplier_id": None,
        "products": [],
        "prices": [],
        "delivery_times": [],
        "quality_metrics": [],
        "past_volumes": [],
        "contract_terms": {}
    }
    
    # Extract supplier name (look for common patterns)
    name_patterns = [
        r'Supplier:\s*([^\n\r]+)',
        r'Vendor:\s*([^\n\r]+)',
        r'Company:\s*([^\n\r]+)',
        r'Contract with\s*([^\n\r]+)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["supplier_name"] = match.group(1).strip()
            break
    
    # Extract prices (look for currency patterns)
    price_pattern = r'[\$€£¥]\s*[\d,]+\.?\d*'
    prices = re.findall(price_pattern, text)
    extracted["prices"] = prices[:10]
    
    # Extract delivery times
    delivery_patterns = [
        r'(\d+)\s*days?\s*delivery',
        r'delivery\s*time:\s*(\d+)\s*days?',
        r'lead\s*time:\s*(\d+)\s*days?',
    ]
    
    for pattern in delivery_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        extracted["delivery_times"].extend([int(m) for m in matches[:5]])
    
    # Extract quality scores
    quality_patterns = [
        r'quality\s*score:\s*(\d+(?:\.\d+)?)',
        r'rating:\s*(\d+(?:\.\d+)?)',
        r'score:\s*(\d+(?:\.\d+)?)',
    ]
    
    for pattern in quality_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        extracted["quality_metrics"].extend([float(m) for m in matches[:5]])
    
    return extracted
