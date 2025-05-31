// main.js
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { promises as fs } from 'fs';
import { fileURLToPath } from 'url';


// for robust find of preload.js, agnostic to app run location
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    }
  });

  // Load SvelteKit dev server for hot-reloading
  win.loadURL('http://localhost:5173');
  // win.webContents.openDevTools();
}


app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});


// main process (main.js) receives message 'load-file-data'
ipcMain.handle('load-file-data', async (event, filePath) => {
  try 
  {
    const data = await fs.readFile(filePath, 'utf-8');
    if (filePath.endsWith('.json')) {
      return JSON.parse(data);
    }
    else {
      return data; 
    }
  } 
  catch (error) 
  {
    console.error('Error reading file in main process:', error);
    // reraise
    throw new Error('Failed to load file data.');
  }
});

