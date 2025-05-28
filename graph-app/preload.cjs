const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  listNodes: () => ipcRenderer.invoke('ls-nodes')
});
