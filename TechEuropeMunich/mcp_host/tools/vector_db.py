"""
Vector Database Service for TactoLearn

This module provides intelligent document processing using ChromaDB for
automatic supplier data extraction and contextual retrieval.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import fitz  # PyMuPDF
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class VectorSupplierDB:
    """Vector database for intelligent supplier document processing"""
    
    def __init__(self, db_path: str = "./vector_db"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create collections
        self.supplier_collection = self.client.get_or_create_collection(
            name="supplier_data",
            metadata={"description": "Supplier documents and data"}
        )
        
        self.conversation_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Negotiation conversations for learning"}
        )
        
        logger.info("Vector database initialized")
    
    async def process_and_store_document(self, file_path: str) -> Dict[str, Any]:
        """
        Automatically process and store a supplier document in vector DB
        Returns extracted supplier profile for immediate use
        """
        try:
            file_path = Path(file_path)
            
            # Generate document ID
            doc_id = self._generate_doc_id(file_path)
            
            # Check if already processed
            existing = self._get_existing_document(doc_id)
            if existing:
                logger.info(f"Document already processed: {file_path.name}")
                return existing
            
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text_content = self._extract_pdf_text(file_path)
            elif file_path.suffix.lower() == '.csv':
                text_content = self._extract_csv_text(file_path)
            else:
                text_content = file_path.read_text(encoding='utf-8')
            
            # Chunk the document for better retrieval
            chunks = self._chunk_document(text_content)
            
            # Extract supplier profile using AI
            supplier_profile = await self._extract_supplier_profile(text_content, chunks)
            
            # Store chunks with embeddings
            await self._store_document_chunks(doc_id, file_path.name, chunks, supplier_profile)
            
            logger.info(f"Successfully processed and stored: {file_path.name}")
            return supplier_profile
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    async def get_contextual_supplier_info(self, query: str, supplier_id: str = None) -> Dict[str, Any]:
        """
        Retrieve contextual supplier information based on query
        Used for generating intelligent responses during negotiation
        """
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search for relevant information
            where_filter = {"supplier_id": supplier_id} if supplier_id else None
            
            results = self.supplier_collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                where=where_filter
            )
            
            # Compile relevant context
            context = {
                "relevant_info": [],
                "supplier_data": {},
                "confidence": 0.0
            }
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0
                    confidence = max(0, 1 - distance)  # Convert distance to confidence
                    
                    context["relevant_info"].append({
                        "content": doc,
                        "confidence": confidence,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                    })
                
                # Extract supplier profile if available
                metadata = results['metadatas'][0][0] if results['metadatas'] and results['metadatas'][0] else {}
                if 'supplier_profile' in metadata:
                    try:
                        context["supplier_data"] = json.loads(metadata['supplier_profile'])
                    except:
                        pass
                
                # Calculate overall confidence
                confidences = [item["confidence"] for item in context["relevant_info"]]
                context["confidence"] = sum(confidences) / len(confidences) if confidences else 0.0
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving contextual info: {str(e)}")
            return {"relevant_info": [], "supplier_data": {}, "confidence": 0.0}
    
    async def store_conversation(self, conversation_data: Dict[str, Any]):
        """Store negotiation conversation for learning and improvement"""
        try:
            conv_id = f"conv_{hashlib.md5(str(conversation_data).encode()).hexdigest()[:8]}"
            
            # Create conversation summary for embedding
            messages = conversation_data.get("messages", [])
            summary = self._create_conversation_summary(messages)
            
            # Store conversation
            embedding = self.embedding_model.encode([summary]).tolist()[0]
            
            self.conversation_collection.add(
                documents=[summary],
                embeddings=[embedding],
                metadatas=[{
                    "conversation_id": conv_id,
                    "supplier_id": conversation_data.get("supplier_id", "unknown"),
                    "timestamp": conversation_data.get("timestamp", ""),
                    "outcome": conversation_data.get("outcome", ""),
                    "strategies_used": json.dumps(conversation_data.get("strategies", [])),
                    "full_conversation": json.dumps(messages)
                }],
                ids=[conv_id]
            )
            
            logger.info(f"Stored conversation: {conv_id}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
    
    def _generate_doc_id(self, file_path: Path) -> str:
        """Generate unique document ID based on file path and modification time"""
        stat = file_path.stat()
        content = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_existing_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Check if document is already processed"""
        try:
            results = self.supplier_collection.get(
                where={"document_id": doc_id},
                limit=1
            )
            
            if results['metadatas'] and results['metadatas'][0]:
                metadata = results['metadatas'][0]
                if 'supplier_profile' in metadata:
                    return json.loads(metadata['supplier_profile'])
            
        except Exception:
            pass
        
        return None
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def _extract_csv_text(self, file_path: Path) -> str:
        """Convert CSV data to structured text"""
        try:
            df = pd.read_csv(file_path)
            
            # Create structured text representation
            text_parts = [f"CSV Data from {file_path.name}:\n"]
            
            # Add column information
            text_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Add sample data
            text_parts.append("\nSample Data:")
            for idx, row in df.head(10).iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
                text_parts.append(f"Row {idx + 1}: {row_text}")
            
            # Add summary statistics
            text_parts.append(f"\nTotal Records: {len(df)}")
            
            # Add numeric summaries
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                text_parts.append("\nNumeric Summaries:")
                for col in numeric_cols:
                    stats = df[col].describe()
                    text_parts.append(f"{col}: min={stats['min']:.2f}, max={stats['max']:.2f}, avg={stats['mean']:.2f}")
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting CSV text: {str(e)}")
            return f"Error processing CSV file: {str(e)}"
    
    def _chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split document into overlapping chunks for better retrieval"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    async def _extract_supplier_profile(self, full_text: str, chunks: List[str]) -> Dict[str, Any]:
        """Extract structured supplier profile using AI"""
        from .llm_service import llm_service
        
        try:
            # Create extraction prompt
            prompt = f"""
            Analyze this supplier document and extract key information for negotiation training.
            
            Document content (first 2000 characters):
            {full_text[:2000]}...
            
            Extract and return ONLY a JSON object with this structure:
            {{
                "supplier_name": "Company name",
                "products": ["list", "of", "products"],
                "services": ["list", "of", "services"],
                "prices": [list of numeric prices found],
                "delivery_times": [list of delivery days/times],
                "quality_metrics": [list of quality scores 0-10],
                "locations": ["list", "of", "locations"],
                "certifications": ["list", "of", "certifications"],
                "payment_terms": ["list", "of", "payment", "terms"],
                "key_strengths": ["strength1", "strength2"],
                "competitive_advantages": ["advantage1", "advantage2"],
                "contact_info": {{"email": "", "phone": "", "address": ""}},
                "negotiation_style": "collaborative|aggressive|defensive|flexible",
                "price_sensitivity": "high|medium|low",
                "volume_discounts": true/false,
                "rush_order_capability": true/false
            }}
            
            Return ONLY the JSON object, no other text.
            """
            
            response = await llm_service._call_llm(prompt)
            
            # Try to parse JSON response
            try:
                profile = json.loads(response)
                
                # Validate and clean the profile
                profile = self._validate_supplier_profile(profile)
                
                return profile
                
            except json.JSONDecodeError:
                logger.warning("Could not parse AI response as JSON, using fallback extraction")
                return self._fallback_extraction(full_text)
                
        except Exception as e:
            logger.error(f"Error in AI extraction: {str(e)}")
            return self._fallback_extraction(full_text)
    
    def _validate_supplier_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted supplier profile"""
        # Ensure required fields exist
        defaults = {
            "supplier_name": "Unknown Supplier",
            "products": [],
            "services": [],
            "prices": [],
            "delivery_times": [],
            "quality_metrics": [],
            "locations": [],
            "certifications": [],
            "payment_terms": [],
            "key_strengths": [],
            "competitive_advantages": [],
            "contact_info": {},
            "negotiation_style": "collaborative",
            "price_sensitivity": "medium",
            "volume_discounts": False,
            "rush_order_capability": False
        }
        
        # Fill missing fields with defaults
        for key, default_value in defaults.items():
            if key not in profile:
                profile[key] = default_value
        
        # Clean numeric fields
        profile["prices"] = [float(p) for p in profile["prices"] if isinstance(p, (int, float)) or str(p).replace('.', '').isdigit()]
        profile["delivery_times"] = [int(d) for d in profile["delivery_times"] if isinstance(d, (int, float)) or str(d).isdigit()]
        profile["quality_metrics"] = [float(q) for q in profile["quality_metrics"] if isinstance(q, (int, float)) and 0 <= float(q) <= 10]
        
        return profile
    
    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback extraction using simple text analysis"""
        import re
        
        profile = {
            "supplier_name": "Unknown Supplier",
            "products": [],
            "services": [],
            "prices": [],
            "delivery_times": [],
            "quality_metrics": [],
            "locations": [],
            "certifications": [],
            "payment_terms": [],
            "key_strengths": [],
            "competitive_advantages": [],
            "contact_info": {},
            "negotiation_style": "collaborative",
            "price_sensitivity": "medium",
            "volume_discounts": False,
            "rush_order_capability": False
        }
        
        # Extract prices using regex
        price_patterns = [r'\$(\d+\.?\d*)', r'(\d+\.?\d*)\s*(?:USD|dollars?)', r'price[:\s]*(\d+\.?\d*)']
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            profile["prices"].extend([float(m) for m in matches if m.replace('.', '').isdigit()])
        
        # Extract delivery times
        delivery_patterns = [r'(\d+)\s*days?', r'delivery[:\s]*(\d+)', r'lead\s*time[:\s]*(\d+)']
        for pattern in delivery_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            profile["delivery_times"].extend([int(m) for m in matches if m.isdigit()])
        
        # Try to find company name
        company_patterns = [r'Company[:\s]*([A-Za-z\s&]+)', r'Supplier[:\s]*([A-Za-z\s&]+)', r'^([A-Z][A-Za-z\s&]{2,30})']
        for pattern in company_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                profile["supplier_name"] = match.group(1).strip()
                break
        
        return profile
    
    async def _store_document_chunks(self, doc_id: str, filename: str, chunks: List[str], supplier_profile: Dict[str, Any]):
        """Store document chunks with embeddings"""
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Prepare metadata for each chunk
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            metadata = {
                "document_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "supplier_id": supplier_profile.get("supplier_name", "unknown"),
                "supplier_profile": json.dumps(supplier_profile)
            }
            
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        # Add to collection
        self.supplier_collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def _create_conversation_summary(self, messages: List[Dict[str, str]]) -> str:
        """Create a summary of conversation for embedding"""
        summary_parts = []
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("message", "")[:200]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")
        
        return " | ".join(summary_parts)

# Global vector database instance
vector_db = VectorSupplierDB()