/**
 * Create an agent using the Beyond Presence API
 * @param {Object} agentData - The agent configuration data
 * @param {string} agentData.name - Display name for the agent (required)
 * @param {string} agentData.avatar_id - ID of avatar to use (required)
 * @param {string} agentData.system_prompt - System prompt for the agent (required)
 * @param {string} [agentData.language] - Language code (e.g., 'en', 'en-US', 'de')
 * @param {string} [agentData.greeting] - What to say when a call starts
 * @param {number} [agentData.max_session_length_minutes] - Max session length (1-90 minutes)
 * @param {Array} [agentData.capabilities] - Extra capabilities (webcam_vision, wakeup_mode)
 * @param {Object} [agentData.llm] - LLM configuration
 * @returns {Promise<Object>} The created agent response
 */
export async function createAgent(agentData) {
  // Support both Vite (frontend) and Node.js (backend) environments

  // Check if we're in a Vite environment (browser) or Node.js environment
  const isViteEnv = typeof import.meta !== 'undefined' && import.meta.env;
  
  let API_KEY = isViteEnv ? import.meta.env.VITE_BEYOND_PRESENCE_API_KEY : process.env.VITE_BEYOND_PRESENCE_API_KEY
  let VITE_BEYOND_PRESENCE_API_BASE_URL = isViteEnv ? import.meta.env.VITE_BEYOND_PRESENCE_API_BASE_URL : process.env.VITE_BEYOND_PRESENCE_API_BASE_URL
  if (!VITE_BEYOND_PRESENCE_API_BASE_URL) {
    VITE_BEYOND_PRESENCE_API_BASE_URL = "https://api.bey.dev/v1/agents"
  }

  let VITE_BEYOND_PRESENCE_AVATAR_ID = isViteEnv ? import.meta.env.VITE_BEYOND_PRESENCE_AVATAR_ID : process.env.VITE_BEYOND_PRESENCE_AVATAR_ID
  
  // Log API key for debugging (first 10 characters only for security)
  console.log('🔑 API Key (first 10 chars):', API_KEY.substring(0, 10) + '...');
  console.log('🌐 API Base URL:', VITE_BEYOND_PRESENCE_API_BASE_URL);
  
  // Required fields validation
  if (!agentData.name || !agentData.avatar_id || !agentData.system_prompt) {
    throw new Error('Missing required fields: name, avatar_id, and system_prompt are required');
  }
  
  // Validate name length
  if (agentData.name.length < 1 || agentData.name.length > 100) {
    throw new Error('Name must be between 1 and 100 characters');
  }
  
  // Validate avatar_id length
  if (agentData.avatar_id.length < 1 || agentData.avatar_id.length > 100) {
    throw new Error('Avatar ID must be between 1 and 100 characters');
  }
  
  // Validate system_prompt length
  if (agentData.system_prompt.length < 1 || agentData.system_prompt.length > 10000) {
    throw new Error('System prompt must be between 1 and 10000 characters');
  }
  
  // Validate greeting length if provided
  if (agentData.greeting && (agentData.greeting.length < 1 || agentData.greeting.length > 1000)) {
    throw new Error('Greeting must be between 1 and 1000 characters');
  }
  
  // Validate max_session_length_minutes if provided
  if (agentData.max_session_length_minutes && 
      (agentData.max_session_length_minutes <= 0 || agentData.max_session_length_minutes > 90)) {
    throw new Error('Max session length must be between 1 and 90 minutes');
  }
  
  const requestBody = {
    name: agentData.name,
    avatar_id: agentData.avatar_id,
    system_prompt: agentData.system_prompt,
    // Optional fields with null checks
    ...(agentData.language && { language: agentData.language }),
    ...(agentData.greeting && { greeting: agentData.greeting }),
    ...(agentData.max_session_length_minutes && { 
      max_session_length_minutes: agentData.max_session_length_minutes 
    }),
    ...(agentData.capabilities && { capabilities: agentData.capabilities }),
    ...(agentData.llm && { llm: agentData.llm })
  };
  
  // Construct the API URL
  const url = VITE_BEYOND_PRESENCE_API_BASE_URL;
  
  // Log request details
  console.log('📤 Making request to:', url);
  console.log('📋 Request body:', JSON.stringify(requestBody, null, 2));
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`API request failed: ${response.status} ${response.statusText}. ${JSON.stringify(errorData)}`);
    }
    
    const agentResponse = await response.json();
    console.log('✅ Agent created successfully:', agentResponse);
    return agentResponse;
    
  } catch (error) {
    console.error('Error creating agent:', error);
    throw error;
  }
}

/**
 * Example usage of the createAgent function
 */
export async function createExampleAgent() {
  const isViteEnv = typeof import.meta !== 'undefined' && import.meta.env;
  let avatarId = isViteEnv ? import.meta.env.VITE_BEYOND_PRESENCE_AVATAR_ID : process.env.VITE_BEYOND_PRESENCE_AVATAR_ID;
  if (!avatarId) {
    avatarId = '694c83e2-8895-4a98-bd16-56332ca3f449';
  }
  
  const exampleAgentData = {
    name: 'Jarvis',
    avatar_id: avatarId,
    system_prompt: 'Talk to me about good holiday destinations.',
    language: 'en',
    greeting: 'Hello, what is your name?',
    max_session_length_minutes: 30,
    capabilities: [
      { type: 'webcam_vision' },
      { 
        type: 'wakeup_mode',
        triggers: ['hey', 'hi', 'hello']
      }
    ],
    llm: {
      type: 'openai'
      // For openai_compatible, you would include:
      // api_id: '01234567-89ab-cdef-0123-456789abcdef',
      // model: 'gpt-4o-mini',
      // temperature: 0.7
    }
  };
  
  try {
    const agent = await createAgent(exampleAgentData);
    console.log('Agent created successfully:', agent);
    return agent;
  } catch (error) {
    console.error('Failed to create agent:', error);
    throw error;
  }
}

// Environment variables required:
// - VITE_BEYOND_PRESENCE_API_KEY: Your Beyond Presence API key (required)
// - VITE_BEYOND_PRESENCE_API_BASE_URL: The Beyond Presence API base URL (optional, defaults to https://api.beyondpresence.com)
// - VITE_BEYOND_PRESENCE_AVATAR_ID: Default avatar ID for examples (optional)
// 
// Add these to your .env file in the project root
