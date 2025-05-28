import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import NodeList from './NodeList.svelte';

const sampleNodes = [
  { id: 'node1', content: [{ type: 'text', value: '<p>Test</p>', metadata: { level: 'beginner' } }] },
  { id: 'node2', content: [{ type: 'code', value: 'echo "test"', metadata: { level: 'intermediate' } }] }
];

describe('NodeList component', () => {
  it('renders nodes', async () => {
    render(NodeList, { props: { nodes: sampleNodes } });
    expect(await screen.findByText('node1')).toBeInTheDocument();
    expect(await screen.findByText('node2')).toBeInTheDocument();
  });

  it('highlights focused index', async () => {
    const { container } = render(NodeList, { props: { nodes: sampleNodes, focusedIndex: 1 } });
    const nodeItems = container.querySelectorAll('.node-item');
    expect(nodeItems[1]).toHaveClass('selected');
    expect(nodeItems[0]).not.toHaveClass('selected');
  });

  it('marks active node', async () => {
    const { container } = render(NodeList, { props: { nodes: sampleNodes, selectedNodeId: 'node1' } });
    const nodeItems = container.querySelectorAll('.node-item');
    expect(nodeItems[0]).toHaveClass('active');
    expect(nodeItems[1]).not.toHaveClass('active');
  });

  it('collapses node', async () => {
    const { container } = render(NodeList, {
      props: { nodes: sampleNodes, collapsedNodes: new Set(['node1']) }
    });
    const nodeItems = container.querySelectorAll('.node-item');
    expect(nodeItems[0]).toHaveClass('collapsed');
    expect(nodeItems[0].querySelector('.content-text')).not.toBeInTheDocument();
    expect(nodeItems[1].querySelector('.content-code')).toBeInTheDocument();
  });
});
