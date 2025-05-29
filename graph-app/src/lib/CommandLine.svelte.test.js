import { render, fireEvent, cleanup, screen } from '@testing-library/svelte'; // screen is useful
import { describe, it, expect, afterEach } from 'vitest';
import CommandLineTestWrapper from './__tests__/helpers/CommandLineTestWrapper.svelte';

afterEach(cleanup);

describe('CommandLine component (via Test Wrapper)', () => {
  it('dispatches the correct command detail on submit and clears input', async () => {
    const { component, container } = render(CommandLineTestWrapper);

    // Use getByPlaceholderText to find the input element reliably
    const inputElement = screen.getByPlaceholderText('Enter command...');
    expect(inputElement).toBeInTheDocument(); // Verify input element is found

    // Get the form element by querying within the rendered container
    // This is robust as CommandLine.svelte defines one form.
    const formElement = container.querySelector('form');
    expect(formElement).toBeInTheDocument(); // Verify form element is found
    // Sanity check that the input is within the form
    expect(formElement.contains(inputElement)).toBe(true);


    const testCommand = 'filter status:active user:deo';
    await fireEvent.input(inputElement, { target: { value: testCommand } });
    expect(inputElement.value).toBe(testCommand);

    // Simulate form submission
    await fireEvent.submit(formElement);

    // Access the captured command from the wrapper's exported prop
    expect(component.lastDispatchedCommandDetail).toBe(testCommand);

    // Assert that the input field (inside CommandLine.svelte) was cleared
    expect(inputElement.value).toBe('');
  });

  it('clears the input after submitting (standalone check)', async () => {
    const { component, container } = render(CommandLineTestWrapper);

    const inputElement = screen.getByPlaceholderText('Enter command...');
    expect(inputElement).toBeInTheDocument();

    const formElement = container.querySelector('form');
    expect(formElement).toBeInTheDocument();
    expect(formElement.contains(inputElement)).toBe(true);


    const anotherCommand = 'test command';
    await fireEvent.input(inputElement, { target: { value: anotherCommand } });
    await fireEvent.submit(formElement);

    expect(inputElement.value).toBe('');
    // Optionally, also check the dispatched command here if the wrapper is used
    expect(component.lastDispatchedCommandDetail).toBe(anotherCommand);
  });
});
