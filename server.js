const express = require('express');
const cors = require('cors');
const path = require('path');
const { spawn } = require('child_process');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Global variables
let pythonProcess = null;
let isBackendRunning = false;

// Start Python backend
function startPythonBackend() {
  if (isBackendRunning) return;
  
  console.log('Starting Python backend...');
  pythonProcess = spawn('python', ['rag-backend/chatbot.py'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log('Python backend:', data.toString());
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Python backend error:', data.toString());
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python backend exited with code ${code}`);
    isBackendRunning = false;
  });

  isBackendRunning = true;
}

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/landing', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/chat', (req, res) => {
  res.sendFile(path.join(__dirname, 'chat.html'));
});

app.get('/chatbot', (req, res) => {
  res.sendFile(path.join(__dirname, 'chatbot.html'));
});

// API Routes
app.get('/api/health', async (req, res) => {
  try {
    const response = await fetch('http://localhost:5000/health');
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.json({ status: 'error', message: 'Backend not available' });
  }
});

app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!isBackendRunning) {
      startPythonBackend();
      // Wait a moment for backend to start
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.json({ 
      status: 'error', 
      message: 'Chat service unavailable',
      error: error.message 
    });
  }
});

app.get('/api/vault-status', (req, res) => {
  // Check if vault directory exists and has content
  const fs = require('fs');
  const vaultPath = path.join(__dirname, 'vault');
  
  try {
    if (fs.existsSync(vaultPath)) {
      const files = fs.readdirSync(vaultPath);
      res.json({ 
        status: 'connected', 
        files: files.length,
        lastSync: new Date().toISOString()
      });
    } else {
      res.json({ status: 'not_found' });
    }
  } catch (error) {
    res.json({ status: 'error', message: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 BuiltByRays™ CFO OS Web Server running on port ${PORT}`);
  console.log(`📱 Access the application at: http://localhost:${PORT}`);
  console.log(`💬 Chat interface: http://localhost:${PORT}/chat`);
  console.log(`🤖 Chatbot interface: http://localhost:${PORT}/chatbot`);
  
  // Start Python backend
  startPythonBackend();
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down server...');
  if (pythonProcess) {
    pythonProcess.kill();
  }
  process.exit(0);
}); 