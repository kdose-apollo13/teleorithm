// src/routes/+page.test.js
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Page from './+page.svelte';

vi.stubGlobal('api', {
  listNodes: vi.fn().mockResolvedValue([
    { id: 'node1', content: [{ type: 'text', value: '<p>Test</p>', metadata: { level: 'beginner' } }] },
    { id: 'node2', content: [{ type: 'code', value: 'echo "test"', metadata: { level: 'intermediate' } }] }
  ])
});

describe('Page component', () => {
  it('starts with CLI focused', async () => {
    const { container } = render(Page);
    await new Promise((r) => setTimeout(r, 100)); // Wait for focus
    const cliContainer = container.querySelector('.cli-container');
    expect(cliContainer).toHaveClass('region-focused');
  });

  it('switches focus to NodeList on Escape', async () => {
    const { container } = render(Page);
    await new Promise((r) => setTimeout(r, 100)); // Wait for initial focus
    await fireEvent.keyDown(window, { key: 'Escape' });
    const nodeListContainer = container.querySelector('.node-list-container');
    expect(nodeListContainer).toHaveClass('region-focused');
  });

  it('navigates NodeList with j/k', async () => {
    const { container } = render(Page);
    await new Promise((r) => setTimeout(r, 100)); // Wait for initial focus
    await fireEvent.keyDown(window, { key: 'Escape' }); // Switch to NodeList
    const nodeItems = container.querySelectorAll('.node-item');
    expect(nodeItems[0]).toHaveClass('selected');
    await fireEvent.keyDown(window, { key: 'j' });
    expect(nodeItems[1]).toHaveClass('selected');
    expect(nodeItems[0]).not.toHaveClass('selected');
  });
});
