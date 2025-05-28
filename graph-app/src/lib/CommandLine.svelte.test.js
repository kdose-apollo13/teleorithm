// src/lib/CommandLine.svelte.test.js
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import CommandLine from './CommandLine.svelte';

describe('CommandLine component', () => {
  it('dispatches command on Enter', async () => {
    let dispatchedCommand = null;
    const { container } = render(CommandLine);
    const input = await screen.findByPlaceholderText('Enter command...');
    const componentRoot = container.querySelector('.cli-input').parentElement;

    componentRoot.addEventListener('command', (e) => console.log('Command Event:', e.detail));
    console.log('Component Root:', componentRoot);
    // Capture custom event on component root
    componentRoot.addEventListener('command', (e) => {
      dispatchedCommand = e.detail;
    });

    await fireEvent.input(input, { target: { value: 'filter beginner' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(dispatchedCommand).toBe('filter beginner');
    expect(input.value).toBe(''); // Verify input clears
  });
});

