// src/routes/+page.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import { tick } from 'svelte';
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
    await new Promise((r) => setTimeout(r, 100));
    const cliContainer = container.querySelector('.cli-container');
    expect(cliContainer).toHaveClass('region-focused');
  });

  it('switches focus to NodeList on Escape', async () => {
    const { container } = render(Page);
    await new Promise((r) => setTimeout(r, 100));
    await fireEvent.keyDown(window, { key: 'Escape' });
    const nodeListContainer = container.querySelector('.node-list-container');
    expect(nodeListContainer).toHaveClass('region-focused');
  });

  it('navigates NodeList with j/k', async () => {
    const { container } = render(Page);
    await new Promise((r) => setTimeout(r, 100));
    await fireEvent.keyDown(window, { key: 'Escape' });
    const nodeItems = container.querySelectorAll('.node-item');
    expect(nodeItems[0]).toHaveClass('selected');
    await fireEvent.keyDown(window, { key: 'j' });
    expect(nodeItems[1]).toHaveClass('selected');
    expect(nodeItems[0]).not.toHaveClass('selected');
  });

  it('handles collapse command', async () => {
    const { container } = render(Page);
    // Wait for nodes to render
    await waitFor(() => {
      const nodeItems = container.querySelectorAll('.node-item');
      expect(nodeItems.length).toBeGreaterThan(0);
    }, { timeout: 1000 });

    const input = screen.getByPlaceholderText('Enter command...');
    const form = input.form;
    await fireEvent.input(input, { target: { value: 'collapse node1' } });
    await fireEvent.submit(form);
    await tick();

    // Wait for collapsed class
    await waitFor(() => {
      const nodeItem = Array.from(container.querySelectorAll('.node-item')).find(
        (item) => item.querySelector('h2')?.textContent === 'node1'
      );
      expect(nodeItem).toHaveClass('collapsed');
    }, { timeout: 1000 });
  });
});
