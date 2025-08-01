const { app, BrowserWindow } = require('electron');
const path = require('path');
const { exec } = require('child_process');

let mainWindow;
let chatbotWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { 
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'assets/logo.png'),
    title: 'BuiltByRAVE CFO OS'
  });
  
  mainWindow.loadFile('index.html');
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

function createChatbotWindow() {
  chatbotWindow = new BrowserWindow({
    width: 500,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    title: 'CFO AI Chatbot'
  });
  
  chatbotWindow.loadFile('chatbot.html');
}

function startBackendServices() {
  // Start the Python backend
  const backendPath = path.join(__dirname, '../rag-backend/chatbot.py');
  const pythonProcess = exec(`python "${backendPath}"`, (error, stdout, stderr) => {
    if (error) {
      console.error('Backend error:', error);
    }
  });
  
  // Start the vault watcher if it exists
  const watcherPath = path.join(__dirname, '../VaultSyncDaemon.exe');
  if (require('fs').existsSync(watcherPath)) {
    exec(`start "" "${watcherPath}"`, (error) => {
      if (error) {
        console.error('Vault watcher error:', error);
      }
    });
  }
}

app.whenReady().then(() => {
  createMainWindow();
  startBackendServices();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle IPC messages
const { ipcMain } = require('electron');

ipcMain.handle('open-chatbot', () => {
  if (!chatbotWindow || chatbotWindow.isDestroyed()) {
    createChatbotWindow();
  } else {
    chatbotWindow.focus();
  }
});

ipcMain.handle('get-backend-status', async () => {
  try {
    const response = await fetch('http://localhost:5000/health');
    return await response.json();
  } catch (error) {
    return { status: 'error', message: error.message };
  }
});

require('dotenv').config();
const apiKey = process.env.OPENAI_API_KEY;
