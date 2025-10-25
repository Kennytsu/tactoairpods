const express = require('express');
const cors = require('cors');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
require('dotenv').config();

const app = express();
const PORT = 3001;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Proxy endpoint for creating agents
app.post('/api/create-agent', async (req, res) => {
  try {
    const API_KEY = process.env.VITE_BEYOND_PRESENCE_API_KEY;
    const API_BASE_URL = process.env.VITE_BEYOND_PRESENCE_API_BASE_URL || 'https://api.bey.dev/v1/agents';
    
    if (!API_KEY) {
      return res.status(500).json({ error: 'API key not configured' });
    }

    console.log('🔑 API Key (first 10 chars):', API_KEY.substring(0, 10) + '...');
    console.log('🌐 API Base URL:', API_BASE_URL);
    console.log('📋 Request body:', JSON.stringify(req.body, null, 2));

    const response = await fetch(API_BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
      },
      body: JSON.stringify(req.body)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`API request failed: ${response.status} ${response.statusText}. ${JSON.stringify(errorData)}`);
    }

    const agentResponse = await response.json();
    console.log('✅ Agent created successfully:', agentResponse);
    res.json(agentResponse);

  } catch (error) {
    console.error('❌ Error creating agent:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Proxy server running on http://localhost:${PORT}`);
  console.log(`📡 CORS-enabled proxy for Beyond Presence API`);
});
