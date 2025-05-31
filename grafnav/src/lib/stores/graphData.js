import { writable } from 'svelte/store';

export const graphData = writable({
  nodes: [
    {
      id: 'node1',
      metadata: 'Metadata for Node 1',
      items: [
        { type: 'Text', level: 1, content: 'Sample text content' },
        { type: 'Code', level: 2, content: 'console.log("Hello");' },
        { type: 'Img', level: 3, content: 'image.jpg' }
      ]
    },
    {
      id: 'node2',
      metadata: 'Metadata for Node 2',
      items: [
        { type: 'Vid', level: 1, content: 'video.mp4' },
        { type: 'Text', level: 2, content: 'More text' }
      ]
    }
  ],
  connections: [
    { from: 'node1', to: 'node2' }
  ]
});
