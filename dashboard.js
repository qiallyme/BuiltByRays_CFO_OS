// BuiltByRays™ CFO OS Dashboard JavaScript

class CFODashboard {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.checkSystemStatus();
        this.loadVaultStatus();
    }

    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendMessage');
        this.chatMessages = document.getElementById('chatMessages');
        this.backendStatus = document.getElementById('backendStatus');
        this.vaultStatus = document.getElementById('vaultStatus');
        this.chatbotStatus = document.getElementById('chatbotStatus');
        this.vaultStatusDisplay = document.getElementById('vaultStatusDisplay');
        this.lastSync = document.getElementById('lastSync');
        this.fileCount = document.getElementById('fileCount');
    }

    bindEvents() {
        // Chat functionality
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Navigation
        document.querySelectorAll('.dashboard-nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToSection(e.target.getAttribute('href').substring(1));
            });
        });
    }

    async checkSystemStatus() {
        try {
            // Check backend API
            const healthResponse = await fetch('/api/health');
            const healthData = await healthResponse.json();
            
            if (healthData.status === 'ok') {
                this.backendStatus.textContent = 'Online';
                this.backendStatus.className = 'status-value online';
                this.chatbotStatus.textContent = 'Available';
                this.chatbotStatus.className = 'status-value online';
            } else {
                this.backendStatus.textContent = 'Offline';
                this.backendStatus.className = 'status-value offline';
                this.chatbotStatus.textContent = 'Unavailable';
                this.chatbotStatus.className = 'status-value offline';
            }
        } catch (error) {
            this.backendStatus.textContent = 'Error';
            this.backendStatus.className = 'status-value error';
            this.chatbotStatus.textContent = 'Error';
            this.chatbotStatus.className = 'status-value error';
        }
    }

    async loadVaultStatus() {
        try {
            const response = await fetch('/api/vault-status');
            const data = await response.json();
            
            if (data.status === 'connected') {
                this.vaultStatus.textContent = 'Connected';
                this.vaultStatus.className = 'status-value online';
                this.vaultStatusDisplay.textContent = 'Connected';
                this.fileCount.textContent = data.files;
                this.lastSync.textContent = new Date(data.lastSync).toLocaleString();
            } else {
                this.vaultStatus.textContent = 'Disconnected';
                this.vaultStatus.className = 'status-value offline';
                this.vaultStatusDisplay.textContent = 'Disconnected';
            }
        } catch (error) {
            this.vaultStatus.textContent = 'Error';
            this.vaultStatus.className = 'status-value error';
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessageToChat('user', message);
        this.messageInput.value = '';

        // Show typing indicator
        this.addTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();

            if (data.status === 'success') {
                this.addMessageToChat('bot', data.response);
            } else {
                this.addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessageToChat('bot', 'Sorry, I\'m having trouble connecting to the server. Please check your connection.');
        }
    }

    addMessageToChat(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const messageP = document.createElement('p');
        messageP.textContent = message;
        messageDiv.appendChild(messageP);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<p>AI is typing...</p>';
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    navigateToSection(sectionId) {
        // Remove active class from all nav links
        document.querySelectorAll('.dashboard-nav a').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to clicked link
        document.querySelector(`a[href="#${sectionId}"]`).classList.add('active');

        // Show the selected section
        document.querySelectorAll('section').forEach(section => {
            section.style.display = 'none';
        });

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CFODashboard();
});

// Add some CSS for the new status indicators
const style = document.createElement('style');
style.textContent = `
    .status-value {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-value.online {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-value.offline {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .status-value.error {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .typing p {
        font-style: italic;
        color: #666;
    }
    
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: #fff;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .dashboard-nav ul {
        display: flex;
        list-style: none;
        gap: 2rem;
    }
    
    .dashboard-nav a {
        text-decoration: none;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    
    .dashboard-nav a.active,
    .dashboard-nav a:hover {
        background-color: #007bff;
        color: white;
    }
    
    .user-menu {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logout-btn {
        padding: 0.5rem 1rem;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .logout-btn:hover {
        background: #c82333;
    }
`;
document.head.appendChild(style); 