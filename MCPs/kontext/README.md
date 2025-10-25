# Kontext MCP Memory Agent

An intelligent agent with persistent memory capabilities powered by the Kontext MCP (Model Context Protocol) server. This agent can store, retrieve, and search through memories, making it perfect for building context-aware AI applications.

## Features

- **Persistent Memory Storage**: Store and retrieve information across sessions
- **Memory Search**: Search through stored memories with natural language queries
- **Context Management**: Maintain conversation contexts and user preferences
- **Interactive CLI**: Easy-to-use command-line interface for memory operations
- **Session Management**: Automatic session handling with the MCP server
- **Conversation History**: Store and retrieve conversation histories

## Prerequisites

- Node.js 18.0.0 or higher
- Kontext API key (get one at [https://kontext.dev](https://kontext.dev))
- A unique user ID for your application

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd kontext-mcp-memory-agent
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:
```env
KONTEXT_API_KEY=your_developer_api_key_here
KONTEXT_USER_ID=your_app_user_id_here
```

## Usage

### Interactive Mode

Run the agent in interactive mode:

```bash
npm start
```

Available commands in interactive mode:
- `store <key> <content>` - Store a memory with a unique key
- `get <key>` - Retrieve a specific memory
- `list` - List all stored memories
- `search <query>` - Search through memories
- `delete <key>` - Delete a specific memory
- `profile` - Get user profile information
- `quit` - Exit the session

### Programmatic Usage

```javascript
import { KontextMCPAgent } from './src/agent.js';

async function main() {
  const agent = new KontextMCPAgent();
  
  // Initialize the agent
  await agent.initialize();
  
  // Store a memory
  await agent.storeMemory('user_preference', 'Prefers dark mode');
  
  // Retrieve a memory
  const preference = await agent.retrieveMemory('user_preference');
  console.log(preference);
  
  // Search memories
  const results = await agent.searchMemories('dark mode');
  console.log(results);
  
  // List all memories
  const memories = await agent.listMemories();
  console.log(memories);
  
  // Clean up
  await agent.terminate();
}

main();
```

### Memory Manager API

The `MemoryManager` class provides advanced memory operations:

```javascript
import { MemoryManager } from './src/memory-manager.js';

// Create memory contexts
await memory.createMemoryContext('user_session', {
  startTime: new Date(),
  preferences: {}
});

// Update memory contexts
await memory.updateMemoryContext('user_session', {
  preferences: { theme: 'dark' }
});

// Store conversations
await memory.storeConversation('conv_123', [
  { role: 'user', content: 'Hello' },
  { role: 'assistant', content: 'Hi there!' }
]);

// Get recent memories
const recent = await memory.getRecentMemories(5);

// Export all memories
const backup = await memory.exportMemories('json');

// Import memories
await memory.importMemories(backupData);
```

## Project Structure

```
kontext-mcp-memory-agent/
├── src/
│   ├── agent.js           # Main agent implementation
│   └── memory-manager.js  # Memory operations wrapper
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
├── package.json          # Node.js dependencies
└── README.md            # This file
```

## How It Works

1. **Authentication**: The agent authenticates with the Kontext MCP server using your API key and user ID
2. **Session Management**: A session is established and maintained throughout the agent's lifecycle
3. **Memory Operations**: All memory operations are performed through the Kontext vault tools
4. **Data Persistence**: Data is securely stored in the Kontext cloud infrastructure

## MCP Server Details

This agent connects to the Kontext MCP server at `https://mcp.kontext.dev/mcp` using:
- Protocol: JSON-RPC 2.0
- Version: 2024-11-05
- Transport: HTTP with SSE for streaming

## Available Tools

The agent uses the following Kontext MCP tools:
- `kontext.vault.listFiles` - List all stored files
- `kontext.vault.readFile` - Read a specific file
- `kontext.vault.writeFile` - Write or update a file
- `kontext.vault.deleteFile` - Delete a file
- `kontext.vault.search` - Search through files
- `kontext.profile.get` - Get user profile information

## Error Handling

The agent includes comprehensive error handling for:
- Authentication failures (invalid API key or user ID)
- Network connectivity issues
- Invalid tool parameters
- Session management errors

Common error codes:
- `-32001`: Unauthorized (check API key and user ID)
- `-32602`: Invalid parameters
- `-32603`: Internal server error

## Development

### Running in Development Mode

```bash
npm run dev
```

This will run the agent with file watching enabled.

### Testing

```bash
npm test
```

## Security Considerations

- Store your API key securely and never commit it to version control
- Use unique user IDs for each user of your application
- The `.gitignore` file is configured to exclude sensitive files
- All data is transmitted over HTTPS

## Troubleshooting

### Authentication Issues
- Verify your API key is correct and active
- Ensure the user ID is properly formatted
- Check that the API URL is accessible

### Connection Issues
- Verify internet connectivity
- Check firewall settings
- Ensure the MCP server endpoint is reachable

### Memory Operations Failing
- Check that the session is properly initialized
- Verify the file paths don't contain invalid characters
- Ensure you have proper permissions for the operation

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues related to:
- The agent implementation: Open an issue in this repository
- Kontext API: Visit [https://kontext.dev/support](https://kontext.dev/support)
- MCP Protocol: Refer to the [MCP documentation](https://modelcontextprotocol.io)