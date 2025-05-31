// preload.js -> common JS
const { contextBridge, ipcRenderer } = require('electron');

// contextBridge isolates preload.js from access to node modules
contextBridge.exposeInMainWorld('electronAPI', {
  loadGraphData: async (filePath) => {
    try 
    {
      // sends message to main process to load data, then returns the data
      const data = await ipcRenderer.invoke('load-file-data', filePath);
      return data;
    } 
    catch (error) 
    {
      console.error('Error in preload during data request:', error);
      return null;
    }
  },
});

