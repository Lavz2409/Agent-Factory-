javascript
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import App from './App';

describe('Calculator App', () => {
  test('renders calculator buttons', () => {
    const { getByText } = render(<App />);
    expect(getByText('1')).toBeInTheDocument();
    expect(getByText('2')).toBeInTheDocument();
    expect(getByText('3')).toBeInTheDocument();
    expect(getByText('+')).toBeInTheDocument();
    expect(getByText('=')).toBeInTheDocument();
  });

  test('performs addition correctly', () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText('1'));
    fireEvent.click(getByText('+'));
    fireEvent.click(getByText('2'));
    fireEvent.click(getByText('='));
    expect(getByText('3')).toBeInTheDocument();
  });

  test('performs subtraction correctly', () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText('5'));
    fireEvent.click(getByText('-'));
    fireEvent.click(getByText('3'));
    fireEvent.click(getByText('='));
    expect(getByText('2')).toBeInTheDocument();
  });

  test('performs multiplication correctly', () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText('4'));
    fireEvent.click(getByText('*'));
    fireEvent.click(getByText('3'));
    fireEvent.click(getByText('='));
    expect(getByText('12')).toBeInTheDocument();
  });

  test('performs division correctly', () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText('8'));
    fireEvent.click(getByText('/'));
    fireEvent.click(getByText('2'));
    fireEvent.click(getByText('='));
    expect(getByText('4')).toBeInTheDocument();
  });

  test('handles division by zero', () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText('8'));
    fireEvent.click(getByText('/'));
    fireEvent.click(getByText('0'));
    fireEvent.click(getByText('='));
    expect(getByText('Error')).toBeInTheDocument();
  });
});