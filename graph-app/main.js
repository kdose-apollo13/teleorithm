// main.js
import { app, BrowserWindow, ipcMain } from 'electron';
import { join } from 'path';
import { promises as fs } from 'fs';

async function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: join(process.cwd(), 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  const isTest = process.env.PLAYWRIGHT_TEST === 'true';
  if (isTest) {
    win.loadFile(join(process.cwd(), 'build', 'index.html'));
  } else {
    win.loadURL('http://localhost:5173').catch(err => {
      console.error('Failed to load URL:', err);
    });
  }

  ipcMain.handle('ls-nodes', async () => {
    try {
      const nodesDir = join(process.cwd(), 'nodes');
      const stats = await fs.stat(nodesDir).catch(() => null);
      if (!stats?.isDirectory()) {
        console.log('No nodes directory found');
        return [];
      }
      const files = await fs.readdir(nodesDir);
      const nodes = await Promise.all(
        files
          .filter(f => f.endsWith('.json'))
          .map(async f => {
            const data = await fs.readFile(join(nodesDir, f), 'utf-8');
            return JSON.parse(data);
          })
      );
      console.log('Nodes loaded:', nodes);
      return nodes;
    } catch (err) {
      console.error('Error listing nodes:', err);
      return [];
    }
  });
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
