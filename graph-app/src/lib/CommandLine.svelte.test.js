import { render, fireEvent, cleanup, screen } from '@testing-library/svelte';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { tick } from 'svelte'; // Import tick for Svelte 5 reactivity cycles if needed

import CommandLineTestWrapper from './__tests__/helpers/CommandLineTestWrapper.svelte';

afterEach(cleanup);

describe('CommandLine component (via Test Wrapper)', () => {
  it('dispatches the correct command detail on form submit and clears input', async () => {
    // `component` is the instance of CommandLineTestWrapper
    const { component, container } = render(CommandLineTestWrapper);

    // Get the input element rendered by CommandLine.svelte (inside the wrapper)
    const inputElement = screen.getByPlaceholderText('Enter command...');
    expect(inputElement).toBeInTheDocument();

    // Get the form element that contains the input
    const formElement = container.querySelector('form'); // Assumes one form in wrapper
    expect(formElement).toBeInTheDocument();
    expect(formElement.contains(inputElement)).toBe(true);


    const testCommand = 'filter status:active user:deo';
    await fireEvent.input(inputElement, { target: { value: testCommand } });
    expect(inputElement.value).toBe(testCommand);

    // Trigger form submission
    // fireEvent.submit should work if the form and its on:submit are correctly set up.
    await fireEvent.submit(formElement);

    // Svelte 5 updates are generally synchronous with fireEvent, but for event dispatch
    // and wrapper updates, a tick might sometimes be needed in complex JSDOM scenarios.
    // Try without it first, add if `lastDispatchedCommandDetail` is still undefined.
    // await tick();

    // Assert that the wrapper's prop was updated by the dispatched event
    expect(component.lastDispatchedCommandDetail).toBe(testCommand);

    // Assert that the input field (inside CommandLine.svelte) was cleared
    expect(inputElement.value).toBe('');
  });

  it('clears the input after submitting (alternative trigger: Enter key)', async () => {
    const { component, container } = render(CommandLineTestWrapper);
    const inputElement = screen.getByPlaceholderText('Enter command...');

    const anotherCommand = 'test command with enter';
    await fireEvent.input(inputElement, { target: { value: anotherCommand } });

    // Simulate pressing Enter on the input field
    await fireEvent.keyDown(inputElement, { key: 'Enter', code: 'Enter', keyCode: 13 });
    // await tick(); // If needed

    expect(inputElement.value).toBe('');
    expect(component.lastDispatchedCommandDetail).toBe(anotherCommand);
  });
});
