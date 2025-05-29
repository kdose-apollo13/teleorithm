// src/lib/CommandLine.svelte.test.js
import { render, fireEvent, cleanup, screen } from '@testing-library/svelte';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { tick } from 'svelte';
import CommandLineTestWrapper from '$tests/helpers/CommandLineTestWrapper.svelte';

afterEach(cleanup);

describe('CommandLine component (via Test Wrapper)', () => {
  it('dispatches the correct command detail via callback and clears input', async () => {
    const commandHandlerMock = vi.fn();
    render(CommandLineTestWrapper, {
      props: {
        onCommandDispatched: commandHandlerMock
      }
    });

    const inputElement = screen.getByPlaceholderText('Enter command...');
    expect(inputElement).toBeInTheDocument();

    const formElement = inputElement.form;
    expect(formElement).toBeInTheDocument();

    const testCommand = 'filter status:active user:deo';
    await fireEvent.input(inputElement, { target: { value: testCommand } });
    expect(inputElement.value).toBe(testCommand);

    await fireEvent.submit(formElement);
    await tick();

    expect(commandHandlerMock).toHaveBeenCalledTimes(1);
    expect(commandHandlerMock).toHaveBeenCalledWith(testCommand);
    expect(inputElement.value).toBe('');
  });

  it('clears the input after submitting with Enter key', async () => {
    const commandHandlerMock = vi.fn();
    render(CommandLineTestWrapper, {
      props: {
        onCommandDispatched: commandHandlerMock
      }
    });

    const inputElement = screen.getByPlaceholderText('Enter command...');
    const formElement = inputElement.form;
    const anotherCommand = 'test command with enter';
    await fireEvent.input(inputElement, { target: { value: anotherCommand } });
    expect(inputElement.value).toBe(anotherCommand);

    // Trigger form submission via Enter key
    await fireEvent.submit(formElement); // Simulate Enter triggering form submit
    await tick();

    expect(commandHandlerMock).toHaveBeenCalledWith(anotherCommand);
    expect(inputElement.value).toBe('');
  });
});
