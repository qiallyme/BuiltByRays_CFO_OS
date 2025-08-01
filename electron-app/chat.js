// Chat Interface JavaScript
class ChatInterface {
    constructor() {
        this.apiUrl = 'http://localhost:5000';
        this.messages = [];
        this.isConnected = false;
        this.typingTimeout = null;
        
        this.initializeElements();
        this.bindEvents();
        this.checkConnection();
        this.loadVaultSections();
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.statusDot = document.getElementById('status-dot');
        this.statusText = document.getElementById('status-text');
        this.vaultPanel = document.getElementById('vault-panel');
        this.vaultSections = document.getElementById('vault-sections');
        this.vaultButton = document.getElementById('vault-button');
        this.closeVaultPanel = document.getElementById('close-vault-panel');
        this.voiceButton = document.getElementById('voice-button');
        this.attachButton = document.getElementById('attach-button');
    }
    
    bindEvents() {
        // Send message
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
        
        // Vault panel
        this.vaultButton.addEventListener('click', () => this.toggleVaultPanel());
        this.closeVaultPanel.addEventListener('click', () => this.toggleVaultPanel());
        
        // Voice button
        this.voiceButton.addEventListener('click', () => this.startVoiceInput());
        
        // Attach button
        this.attachButton.addEventListener('click', () => this.attachFile());
    }
    
    async checkConnection() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.setConnectionStatus(true);
            } else {
                this.setConnectionStatus(false);
            }
        } catch (error) {
            console.error('Connection check failed:', error);
            this.setConnectionStatus(false);
        }
    }
    
    setConnectionStatus(connected) {
        this.isConnected = connected;
        const statusDot = this.statusDot;
        const statusText = this.statusText;
        
        if (connected) {
            statusDot.style.background = '#10b981';
            statusText.textContent = 'Connected';
        } else {
            statusDot.style.background = '#ef4444';
            statusText.textContent = 'Disconnected';
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    client_context: this.getClientContext()
                })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.error) {
                this.addMessage(`Error: ${data.error}`, 'bot');
            } else {
                this.addMessage(data.response, 'bot', data.vault_sections_referenced);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }
    
    addMessage(text, sender, vaultSections = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (sender === 'bot') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = text;
        
        content.appendChild(textDiv);
        
        // Add vault section references if available
        if (vaultSections && vaultSections.length > 0) {
            const sectionsDiv = document.createElement('div');
            sectionsDiv.className = 'vault-references';
            sectionsDiv.innerHTML = '<small>Referenced: ' + vaultSections.join(', ') + '</small>';
            content.appendChild(sectionsDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store message
        this.messages.push({
            sender: sender,
            text: text,
            timestamp: new Date(),
            vaultSections: vaultSections
        });
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    toggleVaultPanel() {
        this.vaultPanel.classList.toggle('open');
    }
    
    async loadVaultSections() {
        const sections = [
            { id: '00', name: 'Home', description: 'Welcome and navigation' },
            { id: '01', name: 'Scope', description: 'Service scope and agreements' },
            { id: '02', name: 'KPIs & Goals', description: 'Key performance indicators and targets' },
            { id: '03', name: 'Payment & Incentives', description: 'Payment terms and structures' },
            { id: '04', name: 'Scenarios & Use Cases', description: 'Real-world scenarios and solutions' },
            { id: '05', name: 'FAQ', description: 'Common questions and answers' },
            { id: '06', name: 'Redline Agreement', description: 'Legal agreements and terms' },
            { id: '07', name: 'Roadmap', description: 'Strategic roadmap and milestones' },
            { id: '08', name: 'Engagements', description: 'Active and completed engagements' },
            { id: '09', name: 'Financials', description: 'Financial data and analysis' },
            { id: '10', name: 'Business Development', description: 'Growth strategies' },
            { id: '11', name: 'Marketing', description: 'Marketing strategies and campaigns' },
            { id: '12', name: 'Operations', description: 'Operational processes' },
            { id: '13', name: 'Human Resources', description: 'HR and team management' },
            { id: '14', name: 'Technology', description: 'Tech infrastructure and tools' },
            { id: '15', name: 'Legal & Compliance', description: 'Legal and compliance matters' },
            { id: '16', name: 'Strategic Initiatives', description: 'Strategic projects' },
            { id: '17', name: 'Client Relations', description: 'Client relationship management' },
            { id: '18', name: 'Performance Analytics', description: 'Performance metrics and insights' }
        ];
        
        this.vaultSections.innerHTML = '';
        
        sections.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'vault-section';
            sectionDiv.innerHTML = `
                <h4>${section.id}-${section.name}</h4>
                <p>${section.description}</p>
            `;
            
            sectionDiv.addEventListener('click', () => {
                this.messageInput.value = `Tell me about ${section.name.toLowerCase()} and what's in section ${section.id}`;
                this.toggleVaultPanel();
            });
            
            this.vaultSections.appendChild(sectionDiv);
        });
    }
    
    getClientContext() {
        // This could be enhanced to include client-specific information
        return "CFO OS Client - BuiltByRays™";
    }
    
    startVoiceInput() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = () => {
                this.voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
                this.voiceButton.style.background = '#ef4444';
                this.voiceButton.style.color = 'white';
            };
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
            };
            
            recognition.onend = () => {
                this.voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
                this.voiceButton.style.background = '';
                this.voiceButton.style.color = '';
            };
            
            recognition.start();
        } else {
            alert('Speech recognition is not supported in this browser.');
        }
    }
    
    attachFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf,.doc,.docx,.txt,.csv,.xlsx';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.addMessage(`Attached: ${file.name}`, 'user');
                // Here you could upload the file to the backend for analysis
            }
        };
        
        input.click();
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
}); 