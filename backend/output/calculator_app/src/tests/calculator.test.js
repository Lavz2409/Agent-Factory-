javascript
// src/tests/calculator.test.js

import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import Calculator from '../components/Calculator';

describe('Calculator Component', () => {
  test('renders Calculator component correctly', () => {
    const { getByText } = render(<Calculator />);
    expect(getByText('0')).toBeInTheDocument();
  });

  test('performs addition correctly', () => {
    const { getByText } = render(<Calculator />);
    fireEvent.click(getByText('1'));
    fireEvent.click(getByText('+'));
    fireEvent.click(getByText('2'));
    fireEvent.click(getByText('='));
    expect(getByText('3')).toBeInTheDocument();
  });

  test('performs subtraction correctly', () => {
    const { getByText } = render(<Calculator />);
    fireEvent.click(getByText('5'));
    fireEvent.click(getByText('-'));
    fireEvent.click(getByText('3'));
    fireEvent.click(getByText('='));
    expect(getByText('2')).toBeInTheDocument();
  });

  test('performs multiplication correctly', () => {
    const { getByText } = render(<Calculator />);
    fireEvent.click(getByText('4'));
    fireEvent.click(getByText('x'));
    fireEvent.click(getByText('3'));
    fireEvent.click(getByText('='));
    expect(getByText('12')).toBeInTheDocument();
  });

  test('performs division correctly', () => {
    const { getByText } = render(<Calculator />);
    fireEvent.click(getByText('8'));
    fireEvent.click(getByText('/'));
    fireEvent.click(getByText('2'));
    fireEvent.click(getByText('='));
    expect(getByText('4')).toBeInTheDocument();
  });

  test('handles division by zero', () => {
    const { getByText } = render(<Calculator />);
    fireEvent.click(getByText('8'));
    fireEvent.click(getByText('/'));
    fireEvent.click(getByText('0'));
    fireEvent.click(getByText('='));
    expect(getByText('Error')).toBeInTheDocument();
  });

  test('clears the display when C is pressed', () => {
    const { getByText } = render(<Calculator />);
    fireEvent.click(getByText('9'));
    fireEvent.click(getByText('C'));
    expect(getByText('0')).toBeInTheDocument();
  });
});