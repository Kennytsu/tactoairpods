import fetch from 'node-fetch';

export class MemoryManager {
  constructor(mcpEndpoint, sessionId, httpsAgent) {
    this.mcpEndpoint = mcpEndpoint;
    this.sessionId = sessionId;
    this.httpsAgent = httpsAgent;
  }

  async callVaultTool(operation, args = {}) {
    const toolName = `kontext.vault.${operation}`;
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
        throw new Error(`Vault operation ${operation} failed: ${JSON.stringify(data.error)}`);
      }

      const result = data.result.content[0].text;
      return result ? JSON.parse(result) : null;
    } catch (error) {
      console.error(`Failed to execute vault operation ${operation}:`, error.message);
      throw error;
    }
  }

  async listFiles() {
    try {
      const result = await this.callVaultTool('listFiles');
      return result || [];
    } catch (error) {
      console.error('Failed to list files:', error.message);
      return [];
    }
  }

  async readFile(path) {
    if (!path) {
      throw new Error('File path is required');
    }

    try {
      // Use query to search for specific file
      const result = await this.callVaultTool('query', { 
        query: path,
        limit: 1 
      });
      return result;
    } catch (error) {
      console.error(`Failed to read file ${path}:`, error.message);
      throw error;
    }
  }

  async writeFile(path, content, metadata = {}) {
    if (!path || content === undefined) {
      throw new Error('File path and content are required');
    }

    // Prepare content as data URI
    const textContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
    const base64Content = Buffer.from(textContent).toString('base64');
    const dataUri = `data:text/plain;base64,${base64Content}`;

    try {
      const result = await this.callVaultTool('upload', {
        fileUri: dataUri,
        fileName: path,
        description: `Memory: ${path} - ${metadata.type || 'general'}`
      });
      return result;
    } catch (error) {
      console.error(`Failed to write file ${path}:`, error.message);
      throw error;
    }
  }

  async deleteFile(path) {
    if (!path) {
      throw new Error('File path is required');
    }

    try {
      const result = await this.callVaultTool('deleteFile', { path });
      return result;
    } catch (error) {
      console.error(`Failed to delete file ${path}:`, error.message);
      throw error;
    }
  }

  async search(query, options = {}) {
    if (!query) {
      throw new Error('Search query is required');
    }

    try {
      // Use the query tool for searching
      const result = await this.callVaultTool('query', {
        query,
        limit: options.limit || 10
      });
      return result || [];
    } catch (error) {
      console.error(`Failed to search with query "${query}":`, error.message);
      throw error;
    }
  }

  async createMemoryContext(contextName, initialData = {}) {
    const contextPath = `contexts/${contextName}.json`;
    const contextData = {
      name: contextName,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      data: initialData,
      history: []
    };

    return await this.writeFile(contextPath, contextData, { type: 'context' });
  }

  async updateMemoryContext(contextName, updates) {
    const contextPath = `contexts/${contextName}.json`;
    
    try {
      const existing = await this.readFile(contextPath);
      const updatedContext = {
        ...existing,
        updated: new Date().toISOString(),
        data: { ...existing.data, ...updates },
        history: [
          ...existing.history,
          {
            timestamp: new Date().toISOString(),
            changes: updates
          }
        ]
      };

      return await this.writeFile(contextPath, updatedContext, { type: 'context' });
    } catch (error) {
      return await this.createMemoryContext(contextName, updates);
    }
  }

  async storeConversation(conversationId, messages) {
    const convPath = `conversations/${conversationId}.json`;
    const conversation = {
      id: conversationId,
      timestamp: new Date().toISOString(),
      messages: messages,
      summary: this.generateSummary(messages)
    };

    return await this.writeFile(convPath, conversation, { type: 'conversation' });
  }

  generateSummary(messages) {
    if (!messages || messages.length === 0) return '';
    
    const topics = new Set();
    const keywords = new Set();
    
    messages.forEach(msg => {
      const words = msg.content.toLowerCase().split(/\s+/);
      words.forEach(word => {
        if (word.length > 4) {
          keywords.add(word);
        }
      });
    });

    return {
      messageCount: messages.length,
      keywords: Array.from(keywords).slice(0, 10),
      firstMessage: messages[0]?.content?.substring(0, 100) || ''
    };
  }

  async getRecentMemories(limit = 10) {
    const files = await this.listFiles();
    
    const memories = await Promise.all(
      files.slice(0, limit).map(async (file) => {
        try {
          const content = await this.readFile(file.path);
          return {
            path: file.path,
            content: content,
            metadata: file.metadata
          };
        } catch (error) {
          return null;
        }
      })
    );

    return memories.filter(m => m !== null);
  }

  async exportMemories(format = 'json') {
    const files = await this.listFiles();
    const memories = {};

    for (const file of files) {
      try {
        memories[file.path] = await this.readFile(file.path);
      } catch (error) {
        console.error(`Failed to export ${file.path}:`, error.message);
      }
    }

    if (format === 'json') {
      return JSON.stringify(memories, null, 2);
    }

    return memories;
  }

  async importMemories(memoriesData) {
    const results = [];
    
    for (const [path, content] of Object.entries(memoriesData)) {
      try {
        await this.writeFile(path, content);
        results.push({ path, success: true });
      } catch (error) {
        results.push({ path, success: false, error: error.message });
      }
    }

    return results;
  }
}