import fetch from 'node-fetch';
import https from 'https';
import dotenv from 'dotenv';

dotenv.config();

async function checkAvailableTools() {
  const httpsAgent = new https.Agent({ rejectUnauthorized: false });
  
  // Initialize session
  const initRequest = {
    jsonrpc: '2.0',
    id: '1',
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: { tools: {}, logging: {} },
      clientInfo: { name: 'kontext-tools-check', version: '1.0.0' }
    }
  };

  const initResponse = await fetch('https://mcp.kontext.dev/mcp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
      'x-kontext-api-key': process.env.KONTEXT_API_KEY,
      'x-kontext-user-id': process.env.KONTEXT_USER_ID
    },
    body: JSON.stringify(initRequest),
    agent: httpsAgent
  });

  const sessionId = initResponse.headers.get('mcp-session-id');
  const text = await initResponse.text();
  
  // Parse SSE response
  let data;
  if (text.startsWith('event:')) {
    const lines = text.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.substring(6);
        try {
          data = JSON.parse(jsonStr);
          break;
        } catch (e) {}
      }
    }
  } else {
    data = JSON.parse(text);
  }

  console.log('Session initialized:', sessionId);
  console.log('\nServer capabilities:', JSON.stringify(data.result.capabilities, null, 2));
  
  // List available tools
  const toolsRequest = {
    jsonrpc: '2.0',
    id: '2',
    method: 'tools/list',
    params: {}
  };

  const toolsResponse = await fetch('https://mcp.kontext.dev/mcp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
      'mcp-session-id': sessionId
    },
    body: JSON.stringify(toolsRequest),
    agent: httpsAgent
  });

  const toolsText = await toolsResponse.text();
  let toolsData;
  
  if (toolsText.startsWith('event:')) {
    const lines = toolsText.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.substring(6);
        try {
          toolsData = JSON.parse(jsonStr);
          break;
        } catch (e) {}
      }
    }
  } else {
    toolsData = JSON.parse(toolsText);
  }

  console.log('\nAvailable tools:');
  if (toolsData.result && toolsData.result.tools) {
    toolsData.result.tools.forEach(tool => {
      console.log(`- ${tool.name}: ${tool.description || 'No description'}`);
    });
  } else {
    console.log('No tools found or error:', toolsData);
  }

  // Clean up
  await fetch('https://mcp.kontext.dev/mcp', {
    method: 'DELETE',
    headers: { 'mcp-session-id': sessionId },
    agent: httpsAgent
  });
}

checkAvailableTools().catch(console.error);