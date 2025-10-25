import { KontextMCPAgent } from './src/agent.js';

async function testAgent() {
  console.log('=== Testing Kontext MCP Memory Agent ===\n');
  
  const agent = new KontextMCPAgent();
  
  try {
    // Initialize
    await agent.initialize();
    console.log('\n✓ Agent initialized successfully\n');
    
    // Test storing memory
    console.log('1. Storing a test memory...');
    await agent.storeMemory('test_greeting', 'Hello from Kontext Memory Agent!');
    console.log('✓ Memory stored\n');
    
    // Test listing memories
    console.log('2. Listing all memories...');
    const files = await agent.listMemories();
    console.log('Memories found:', files);
    console.log('');
    
    // Test retrieving memory
    console.log('3. Retrieving the test memory...');
    const content = await agent.retrieveMemory('test_greeting');
    console.log('Retrieved content:', content);
    console.log('');
    
    // Store another memory with metadata
    console.log('4. Storing memory with metadata...');
    await agent.storeMemory('user_context', {
      timestamp: new Date().toISOString(),
      preferences: {
        theme: 'dark',
        language: 'en'
      },
      sessionInfo: 'Demo session for TechEurope'
    });
    console.log('✓ Context memory stored\n');
    
    // List files again to see both
    console.log('5. Listing all memories again...');
    const allFiles = await agent.listMemories();
    console.log('All memories:', JSON.stringify(allFiles, null, 2));
    console.log('');
    
    // Search memories
    console.log('6. Searching memories for "greeting"...');
    const searchResults = await agent.searchMemories('greeting');
    console.log('Search results:', searchResults);
    console.log('');
    
    console.log('=== All tests completed successfully! ===');
    
  } catch (error) {
    console.error('Test failed:', error.message);
  } finally {
    await agent.terminate();
    process.exit(0);
  }
}

testAgent();