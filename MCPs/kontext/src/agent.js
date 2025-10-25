import dotenv from 'dotenv';
import fetch from 'node-fetch';
import https from 'https';
import readline from 'readline';
import { MemoryManager } from './memory-manager.js';

dotenv.config();

class KontextMCPAgent {
  constructor() {
    this.apiKey = process.env.KONTEXT_API_KEY;
    this.userId = process.env.KONTEXT_USER_ID;
    this.apiUrl = process.env.KONTEXT_API_URL || 'https://staging-api.kontext.dev';
    this.mcpEndpoint = 'https://mcp.kontext.dev/mcp';
    this.sessionId = null;
    this.memory = null;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    // Create HTTPS agent with relaxed SSL for development
    this.httpsAgent = new https.Agent({
      rejectUnauthorized: false
    });
  }

  async initialize() {
    console.log('Initializing Kontext MCP Agent...');
    
    const initRequest = {
      jsonrpc: '2.0',
      id: '1',
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {}, logging: {} },
        clientInfo: { name: 'kontext-memory-agent', version: '1.0.0' }
      }
    };

    try {
      const response = await fetch(this.mcpEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream',
          'x-kontext-api-key': this.apiKey,
          'x-kontext-user-id': this.userId,
          'x-kontext-api-url': this.apiUrl
        },
        body: JSON.stringify(initRequest),
        agent: this.httpsAgent
      });

      this.sessionId = response.headers.get('mcp-session-id');
      
      // Handle SSE response
      const text = await response.text();
      let data;
      
      // Check if response is SSE format
      if (text.startsWith('event:')) {
        // Parse SSE format
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.substring(6);
            try {
              data = JSON.parse(jsonStr);
              break;
            } catch (e) {
              // Continue to next line
            }
          }
        }
      } else {
        // Regular JSON response
        data = JSON.parse(text);
      }
      
      if (data.error) {
        throw new Error(`Initialization failed: ${JSON.stringify(data.error)}`);
      }

      console.log('Agent initialized successfully');
      console.log('Session ID:', this.sessionId);
      
      this.memory = new MemoryManager(this.mcpEndpoint, this.sessionId, this.httpsAgent);
      
      return data.result;
    } catch (error) {
      console.error('Failed to initialize agent:', error.message);
      throw error;
    }
  }

  async callTool(toolName, args = {}) {
    if (!this.sessionId) {
      throw new Error('Agent not initialized. Call initialize() first.');
    }

    const toolRequest = {
      jsonrpc: '2.0',
      id: Date.now().toString(),
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args
      }
    };

    try {
      const response = await fetch(this.mcpEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream',
          'mcp-session-id': this.sessionId
        },
        body: JSON.stringify(toolRequest),
        agent: this.httpsAgent
      });

      // Handle SSE response
      const text = await response.text();
      let data;
      
      if (text.startsWith('event:')) {
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.substring(6);
            try {
              data = JSON.parse(jsonStr);
              break;
            } catch (e) {
              // Continue to next line
            }
          }
        }
      } else {
        data = JSON.parse(text);
      }
      
      if (data.error) {
        throw new Error(`Tool call failed: ${JSON.stringify(data.error)}`);
      }

      return JSON.parse(data.result.content[0].text);
    } catch (error) {
      console.error(`Failed to call tool ${toolName}:`, error.message);
      throw error;
    }
  }

  async storeMemory(key, content, metadata = {}) {
    console.log(`Storing memory: ${key}`);
    return await this.memory.writeFile(key, content, metadata);
  }

  async retrieveMemory(key) {
    console.log(`Retrieving memory: ${key}`);
    return await this.memory.readFile(key);
  }

  async listMemories() {
    console.log('Listing all memories...');
    return await this.memory.listFiles();
  }

  async searchMemories(query) {
    console.log(`Searching memories for: ${query}`);
    return await this.memory.search(query);
  }

  async deleteMemory(key) {
    console.log(`Deleting memory: ${key}`);
    return await this.memory.deleteFile(key);
  }

  async interactiveSession() {
    console.log('\n=== Kontext Memory Agent Interactive Session ===');
    console.log('Commands:');
    console.log('  store <key> <content> - Store a memory');
    console.log('  get <key> - Retrieve a memory');
    console.log('  list - List all memories');
    console.log('  search <query> - Search memories');
    console.log('  delete <key> - Delete a memory');
    console.log('  profile - Get user profile');
    console.log('  quit - Exit the session\n');

    const processCommand = async (input) => {
      const [command, ...args] = input.trim().split(' ');

      try {
        switch (command.toLowerCase()) {
          case 'store':
            if (args.length < 2) {
              console.log('Usage: store <key> <content>');
              break;
            }
            const storeKey = args[0];
            const storeContent = args.slice(1).join(' ');
            await this.storeMemory(storeKey, storeContent);
            console.log(`Memory stored successfully: ${storeKey}`);
            break;

          case 'get':
            if (args.length < 1) {
              console.log('Usage: get <key>');
              break;
            }
            const getResult = await this.retrieveMemory(args[0]);
            console.log('Memory content:', getResult);
            break;

          case 'list':
            const files = await this.listMemories();
            console.log('Stored memories:', files);
            break;

          case 'search':
            if (args.length < 1) {
              console.log('Usage: search <query>');
              break;
            }
            const searchQuery = args.join(' ');
            const searchResults = await this.searchMemories(searchQuery);
            console.log('Search results:', searchResults);
            break;

          case 'delete':
            if (args.length < 1) {
              console.log('Usage: delete <key>');
              break;
            }
            await this.deleteMemory(args[0]);
            console.log(`Memory deleted: ${args[0]}`);
            break;

          case 'profile':
            const profile = await this.callTool('kontext.profile.get');
            console.log('User profile:', profile);
            break;

          case 'quit':
          case 'exit':
            await this.terminate();
            process.exit(0);
            break;

          default:
            console.log('Unknown command. Type a valid command or "quit" to exit.');
        }
      } catch (error) {
        console.error('Error:', error.message);
      }

      this.rl.question('> ', processCommand);
    };

    this.rl.question('> ', processCommand);
  }

  async terminate() {
    if (this.sessionId) {
      console.log('Terminating session...');
      await fetch(this.mcpEndpoint, {
        method: 'DELETE',
        headers: {
          'mcp-session-id': this.sessionId
        },
        agent: this.httpsAgent
      });
      this.sessionId = null;
    }
    this.rl.close();
  }
}

async function main() {
  if (!process.env.KONTEXT_API_KEY || !process.env.KONTEXT_USER_ID) {
    console.error('Error: KONTEXT_API_KEY and KONTEXT_USER_ID must be set in .env file');
    process.exit(1);
  }

  const agent = new KontextMCPAgent();
  
  try {
    await agent.initialize();
    await agent.interactiveSession();
  } catch (error) {
    console.error('Fatal error:', error.message);
    await agent.terminate();
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { KontextMCPAgent };