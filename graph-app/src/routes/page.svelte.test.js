// src/routes/+page.test.js
import { render, screen } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Page from './+page.svelte';

// Mock window.api
const mockNodes = [
  { id: 'node1', content: [{ type: 'text', value: '<p>Test</p>', metadata: { level: 'beginner' } }] },
  { id: 'node2', content: [{ type: 'code', value: 'echo "test"', metadata: { level: 'intermediate' } }] }
];

vi.stubGlobal('api', {
  listNodes: vi.fn().mockResolvedValue(mockNodes)
});

describe('Page component', () => {
  it('renders the node list with nodes', async () => {
    render(Page);
    expect(await screen.findByRole('listbox', { name: 'Node List' })).toBeInTheDocument();
    expect(await screen.findByText('node1')).toBeInTheDocument();
    expect(await screen.findByText('node2')).toBeInTheDocument();
  });
});
