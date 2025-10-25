# 🤝 Negotiation Training Agent – Hackathon Project

## 📌 Context
This project is being developed as part of the **Munich Hack 2025** competition.  
Our customer is **Tacto**, a procurement platform. Tacto currently provides a static, 3-page negotiation dossier to its customers. While helpful, the dossier is impersonal, text-heavy, and doesn’t prepare users for the *actual conversational dynamics* of negotiations.  

We aim to create an **interactive negotiation training agent** that allows users to practice real-world negotiation scenarios through natural voice conversations with an avatar.

---

## 🛑 Problem We Are Solving
- Negotiation dossiers are **static** → users passively read them instead of *experiencing* negotiation practice.  
- Negotiations are inherently **conversational and dynamic** → current tools do not reflect this.  
- Customers need to **train negotiation skills interactively**, adapting to counter-offers and strategies in real time.  

**Our goal:** Replace the static dossier with a **personalized, conversational training experience** where users can speak to an AI-powered avatar that plays the role of their counterpart.

---

## 💡 Solution Overview
We are building a **web-embeddable conversational agent** powered by:

1. **Speech-to-Text (STT)** → Captures the user’s spoken input (German/English).  
2. **Conversational Agent (LLM)** → Processes user input with full access to the negotiation dossier & customer context.  
3. **BEY Avatar API** → Turns the AI’s response into natural speech and lip-synced video of a virtual negotiator.  
4. **Embeddable Web UI** → Provides a persistent avatar that remains present across the conversation, creating a realistic role-play environment.  

---

## 🛠️ Implementation Approach

### 🎙️ Input Processing
- Users speak into their microphone (via browser).  
- Audio is transcribed using STT (e.g., Whisper API).  
- Transcribed text is forwarded to the conversational agent.  

### 🧠 Conversational Agent
- Built around an **Agent with memory** (not just a raw LLM).  
- Maintains multi-turn context:  
  - Tracks offers, counter-offers, concessions.  
  - Uses a **system prompt** that defines the negotiation style (assertive, collaborative, etc.).  
- Negotiation dossier + customer data is injected as additional context.  

### 🛠️ Future Enhancement: MCP Tools
- Tools that allow the agent to:  
  - Fetch structured dossier data on demand.  
  - Enforce constraints (e.g., max discount, deadlines).  
  - Perform calculations (margins, trade-offs).  
- Adds realism by preventing hallucinations and simulating real limits.  

### 🧑‍💻 BEY Agent Integration
- Create a **persistent BEY Agent session** via API:  
  - `avatar_id` → which face to use.  
  - `system_prompt` → negotiation persona.  
- Use BEY’s **embeddable iframe widget** to keep the avatar continuously visible in the UI.  
- Each LLM response is sent as text to the same agent session → BEY streams synchronized video/audio back.  

**Example Agent Creation (BEY API):**
```bash
curl --request POST \
  --url https://api.bey.dev/v1/agent \
  --header 'Authorization: Bearer $BEY_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "avatar_id": "example_avatar_id",
    "system_prompt": "You are a tough but fair procurement negotiator. Stick to the dossier and never concede more than 5%."
  }'
