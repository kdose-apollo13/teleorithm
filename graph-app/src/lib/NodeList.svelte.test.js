// src/lib/NodeList.svelte.test.js
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import NodeList from './NodeList.svelte';

const sampleNodes = [
  {
    id: 'node1',
    content: [{ type: 'text', value: '<p>Test</p>', metadata: { level: 'beginner' } }]
  },
  {
    id: 'node2',
    content: [{ type: 'code', value: 'echo "test"', metadata: { level: 'intermediate' } }]
  }
];

describe('NodeList component', () => {
  it('renders nodes', async () => {
    render(NodeList, { props: { nodes: sampleNodes } });
    expect(await screen.findByText('node1')).toBeInTheDocument();
    expect(await screen.findByText('node2')).toBeInTheDocument();
  });

  it('navigates with j/k keys', async () => {
    const { container } = render(NodeList, { props: { nodes: sampleNodes } });
    expect(container.querySelectorAll('.node-item')[0]).toHaveClass('selected');
    await fireEvent.keyDown(window, { key: 'j' });
    expect(container.querySelectorAll('.node-item')[1]).toHaveClass('selected');
    await fireEvent.keyDown(window, { key: 'k' });
    expect(container.querySelectorAll('.node-item')[0]).toHaveClass('selected');
  });

  it('toggles selection with Enter', async () => {
    const { container } = render(NodeList, { props: { nodes: sampleNodes } });
    await fireEvent.keyDown(window, { key: 'Enter' });
    expect(container.querySelectorAll('.node-item')[0]).toHaveClass('active');
    await fireEvent.keyDown(window, { key: 'Enter' });
    expect(container.querySelectorAll('.node-item')[0]).not.toHaveClass('active');
  });

  it('toggles collapse with Space', async () => {
    const { container } = render(NodeList, { props: { nodes: sampleNodes } });
    const nodeItem = container.querySelectorAll('.node-item')[0];
    await fireEvent.keyDown(window, { key: ' ' });
    expect(nodeItem).toHaveClass('collapsed');
    expect(nodeItem.querySelector('.content-text')).toBeNull();
    await fireEvent.keyDown(window, { key: ' ' });
    expect(nodeItem).not.toHaveClass('collapsed');
    expect(nodeItem.querySelector('.content-text')).toBeInTheDocument();
  });
});
