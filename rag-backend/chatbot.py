import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from embedder import embed_documents, query_vector_store
import openai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI with error handling
def get_openai_key():
    """Get OpenAI API key with proper error handling"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables")
        print("   Please set your OpenAI API key in a .env file or environment variable")
        return None
    return api_key

openai.api_key = get_openai_key()

class CFOAIChatbot:
    def __init__(self):
        self.conversation_history = []
        self.vault_knowledge = self.load_vault_knowledge()
    
    def load_vault_knowledge(self):
        """Load and embed all vault documents"""
        try:
            embed_documents()
            return "Vault knowledge loaded successfully"
        except Exception as e:
            return f"Error loading vault: {str(e)}"
    
    def get_relevant_context(self, query):
        """Get relevant context from vault"""
        try:
            results = query_vector_store(query)
            if results and len(results) > 0:
                return "\n\n".join(results[0])
            return ""
        except Exception as e:
            return f"Error querying vault: {str(e)}"
    
    def generate_response(self, user_message, client_context=""):
        """Generate AI response with vault knowledge"""
        
        # Check if OpenAI API key is available
        if not openai.api_key:
            return {
                "response": "I apologize, but the OpenAI API key is not configured. Please set your OPENAI_API_KEY environment variable and restart the application.",
                "vault_sections_referenced": [],
                "confidence": "low"
            }
        
        # Get relevant context from vault
        vault_context = self.get_relevant_context(user_message)
        
        # Build system prompt
        system_prompt = f"""You are a CFO AI Assistant for BuiltByRays™. You have access to the client's complete financial operating system vault.

AVAILABLE VAULT SECTIONS:
- 00-Home: Welcome and navigation
- 01-Scope: Service scope and agreements
- 02-KPIs_Goals: Key performance indicators and targets
- 03-Payment_Incentives: Payment terms and structures
- 04-Scenarios_UseCases: Real-world scenarios and solutions
- 05-FAQ: Common questions and answers
- 06-Redline_Agreement: Legal agreements and terms
- 07-Roadmap: Strategic roadmap and milestones
- 08-Engagements: Active and completed engagements
- 09-Financials: Financial data and analysis
- 10-Business_Development: Growth strategies
- 11-Marketing: Marketing strategies and campaigns
- 12-Operations: Operational processes
- 13-Human_Resources: HR and team management
- 14-Technology: Tech infrastructure and tools
- 15-Legal_Compliance: Legal and compliance matters
- 16-Strategic_Initiatives: Strategic projects
- 17-Client_Relations: Client relationship management
- 18-Performance_Analytics: Performance metrics and insights

CLIENT CONTEXT: {client_context}

RELEVANT VAULT CONTENT:
{vault_context}

INSTRUCTIONS:
1. Answer based on the vault knowledge first
2. If information isn't in the vault, provide general CFO guidance
3. Always be helpful, professional, and actionable
4. Suggest next steps when appropriate
5. Reference specific vault sections when relevant
6. If you need to update the vault, mention what should be added

CONVERSATION HISTORY:
{self.format_conversation_history()}

USER MESSAGE: {user_message}

RESPONSE:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Log the interaction
            self.log_interaction(user_message, ai_response, vault_context)
            
            return {
                "response": ai_response,
                "vault_sections_referenced": self.extract_vault_references(ai_response),
                "confidence": "high" if vault_context else "medium"
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again or contact support.",
                "vault_sections_referenced": [],
                "confidence": "low"
            }
    
    def format_conversation_history(self):
        """Format conversation history for context"""
        if len(self.conversation_history) > 10:
            history = self.conversation_history[-10:]
        else:
            history = self.conversation_history
        
        formatted = []
        for entry in history:
            formatted.append(f"User: {entry['user']}")
            formatted.append(f"Assistant: {entry['assistant']}")
        
        return "\n".join(formatted)
    
    def extract_vault_references(self, response):
        """Extract vault section references from response"""
        sections = []
        for i in range(19):
            section_num = f"{i:02d}"
            if f"{section_num}-" in response:
                sections.append(f"{section_num}")
        return sections
    
    def log_interaction(self, user_message, ai_response, vault_context):
        """Log the interaction for analytics"""
        log_entry = {
            "timestamp": str(datetime.now()),
            "user_message": user_message,
            "ai_response": ai_response,
            "vault_context_used": bool(vault_context),
            "vault_context_length": len(vault_context)
        }
        
        # Save to log file
        try:
            with open("chatbot_logs.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
        
        # Add to conversation history
        self.conversation_history.append({
            "user": user_message,
            "assistant": ai_response
        })

# Initialize chatbot
chatbot = CFOAIChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        client_context = data.get('client_context', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        response = chatbot.generate_response(user_message, client_context)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vault/query', methods=['POST'])
def query_vault():
    """Direct vault query endpoint"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        results = query_vector_store(query)
        return jsonify({"results": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vault/update', methods=['POST'])
def update_vault():
    """Update vault knowledge base"""
    try:
        # Re-embed documents
        embed_documents()
        return jsonify({"message": "Vault updated successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "vault_loaded": bool(chatbot.vault_knowledge),
        "openai_configured": bool(openai.api_key)
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with basic info"""
    return jsonify({
        "message": "BuiltByRays™ CFO OS Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "vault_query": "/vault/query",
            "vault_update": "/vault/update"
        }
    })

if __name__ == '__main__':
    print("Starting CFO AI Chatbot...")
    print(f"Vault status: {chatbot.vault_knowledge}")
    
    if not openai.api_key:
        print("⚠️  WARNING: OpenAI API key not configured")
        print("   The chatbot will start but AI responses will be limited")
    
    print("🌐 Server will be available at: http://localhost:5000")
    print("💬 Chat interface: http://localhost:5000/chat")
    print("📊 Health check: http://localhost:5000/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 