const { app, BrowserWindow } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

function startVaultWatcher() {
  const watcherPath = path.join(__dirname, '../VaultSyncDaemon.exe');
  if (fs.existsSync(watcherPath)) {
    exec(`start "" "${watcherPath}"`);
  }
}

function startBackend() {
  const backendPath = path.join(__dirname, '../rag-backend/chatbot.py');
  exec(`start "" python "${backendPath}"`);
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'electron-app/assets/logo.png'),
    title: 'BuiltByRays™ CFO OS'
  });
  
  win.loadFile('electron-app/index.html');
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    win.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
