const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

// Optional: For Node < 18
let fetch;
try {
  fetch = global.fetch || require('node-fetch');
} catch (e) {
  console.warn('Fetch not available and node-fetch not installed');
}

require('dotenv').config();
const apiKey = process.env.OPENAI_API_KEY;

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
    title: 'BuiltByRays™ CFO OS'
  });
  
  mainWindow.loadFile('index.html');

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
  // Start Python backend
  const backendPath = path.join(__dirname, '../rag-backend/chatbot.py');
  const pythonProcess = exec(`python "${backendPath}"`, (error) => {
    if (error) console.error('Backend error:', error);
  });
  
  // Start vault sync daemon
  const watcherPath = path.join(__dirname, '../VaultSyncDaemon.exe');
  if (fs.existsSync(watcherPath)) {
    const watcherProcess = exec(`"${watcherPath}"`, (error) => {
      if (error) console.error('Vault watcher error:', error);
    });
  }
  
  // Start setup script if needed
  const setupPath = path.join(__dirname, '../setup.py');
  if (fs.existsSync(setupPath)) {
    exec(`python "${setupPath}"`, (error) => {
      if (error) console.error('Setup error:', error);
    });
  }
}

app.whenReady().then(() => {
  // Set app to autostart on login (Windows)
  if (process.platform === 'win32') {
    app.setLoginItemSettings({
      openAtLogin: true,
      path: process.execPath,
      args: []
    });
  }

  createMainWindow();
  startBackendServices();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC Handlers
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
