import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import CommandLine from './CommandLine.svelte';

describe('CommandLine component', () => {
  it('clears the input after submitting', async () => {
    const { getByPlaceholderText } = render(CommandLine);
    const input = getByPlaceholderText('Enter command...');

    await fireEvent.input(input, { target: { value: 'test command' } });
    await fireEvent.submit(input.form);

    expect(input.value).toBe('');
  });
});
