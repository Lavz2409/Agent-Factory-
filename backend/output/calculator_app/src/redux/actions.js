javascript
// src/redux/actions.js

// Action Types
export const ADD_DIGIT = 'ADD_DIGIT';
export const PERFORM_OPERATION = 'PERFORM_OPERATION';

// Action Creators

/**
 * Creates an action to add a digit to the current input.
 * @param {String} digit - The digit to add.
 * @returns {Object} The action object.
 */
export function addDigit(digit) {
  return {
    type: ADD_DIGIT,
    payload: digit
  };
}

/**
 * Creates an action to perform a calculator operation.
 * @param {String} operation - The operation to perform (e.g., '+', '-', '*', '/').
 * @returns {Object} The action object.
 */
export function performOperation(operation) {
  return {
    type: PERFORM_OPERATION,
    payload: operation
  };
}