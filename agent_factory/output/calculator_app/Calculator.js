javascript
import React, { useState } from 'react';
import './Calculator.css';

const Calculator = () => {
  const [expression, setExpression] = useState('');
  const [result, setResult] = useState(0);

  const handleButtonClick = (value) => {
    setExpression((prev) => prev + value);
  };

  const calculateResult = (expression) => {
    try {
      // Using eval is generally unsafe, but for simplicity in this example, we use it.
      // In a real-world scenario, consider using a math library or a custom parser.
      const evaluatedResult = eval(expression);
      setResult(evaluatedResult);
    } catch (error) {
      setResult('Error');
    }
  };

  const handleClear = () => {
    setExpression('');
    setResult(0);
  };

  const handleEquals = () => {
    calculateResult(expression);
  };

  return (
    <div className="calculator">
      <div className="display">
        <div className="expression">{expression}</div>
        <div className="result">{result}</div>
      </div>
      <div className="buttons">
        <button onClick={() => handleButtonClick('1')}>1</button>
        <button onClick={() => handleButtonClick('2')}>2</button>
        <button onClick={() => handleButtonClick('3')}>3</button>
        <button onClick={() => handleButtonClick('+')}>+</button>
        <button onClick={() => handleButtonClick('4')}>4</button>
        <button onClick={() => handleButtonClick('5')}>5</button>
        <button onClick={() => handleButtonClick('6')}>6</button>
        <button onClick={() => handleButtonClick('-')}>-</button>
        <button onClick={() => handleButtonClick('7')}>7</button>
        <button onClick={() => handleButtonClick('8')}>8</button>
        <button onClick={() => handleButtonClick('9')}>9</button>
        <button onClick={() => handleButtonClick('*')}>*</button>
        <button onClick={() => handleButtonClick('0')}>0</button>
        <button onClick={() => handleButtonClick('.')}>.</button>
        <button onClick={handleEquals}>=</button>
        <button onClick={() => handleButtonClick('/')}>/</button>
        <button onClick={handleClear}>C</button>
      </div>
    </div>
  );
};

export default Calculator;