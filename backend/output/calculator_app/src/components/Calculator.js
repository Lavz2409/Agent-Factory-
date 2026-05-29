javascript
import React, { useState } from 'react';
import styled from 'styled-components';

const CalculatorContainer = styled.div`
  width: 300px;
  margin: 50px auto;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
`;

const Display = styled.div`
  width: 100%;
  height: 50px;
  background-color: #222;
  color: #fff;
  font-size: 2em;
  text-align: right;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 5px;
  margin-bottom: 10px;
`;

const ButtonGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
`;

const Button = styled.button`
  padding: 20px;
  font-size: 1.2em;
  border: none;
  border-radius: 5px;
  background-color: #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #d0d0d0;
  }

  &:active {
    background-color: #c0c0c0;
  }
`;

const Calculator = () => {
  const [displayValue, setDisplayValue] = useState('');
  
  const handleButtonClick = (value) => {
    if (value === '=') {
      try {
        setDisplayValue(eval(displayValue).toString());
      } catch {
        setDisplayValue('Error');
      }
    } else if (value === 'C') {
      setDisplayValue('');
    } else {
      setDisplayValue(displayValue + value);
    }
  };

  const buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', '.', '=', '+',
    'C'
  ];

  return (
    <CalculatorContainer>
      <Display>{displayValue}</Display>
      <ButtonGrid>
        {buttons.map((button) => (
          <Button key={button} onClick={() => handleButtonClick(button)}>
            {button}
          </Button>
        ))}
      </ButtonGrid>
    </CalculatorContainer>
  );
};

export default Calculator;