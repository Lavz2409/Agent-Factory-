javascript
import { createStore } from 'redux';

// Initial state of the calculator
const initialState = {
  displayValue: '0',
  previousValue: null,
  operation: null,
  waitingForNewValue: false
};

// Reducer function to handle state changes
function calculatorReducer(state = initialState, action) {
  switch (action.type) {
    case 'INPUT_DIGIT':
      if (state.waitingForNewValue) {
        return {
          ...state,
          displayValue: action.digit,
          waitingForNewValue: false
        };
      }
      return {
        ...state,
        displayValue: state.displayValue === '0' ? action.digit : state.displayValue + action.digit
      };

    case 'INPUT_DECIMAL':
      if (state.waitingForNewValue) {
        return {
          ...state,
          displayValue: '0.',
          waitingForNewValue: false
        };
      }
      if (!state.displayValue.includes('.')) {
        return {
          ...state,
          displayValue: state.displayValue + '.'
        };
      }
      return state;

    case 'CLEAR_DISPLAY':
      return initialState;

    case 'PERFORM_OPERATION':
      if (state.operation && state.waitingForNewValue) {
        return {
          ...state,
          operation: action.operation
        };
      }

      const inputValue = parseFloat(state.displayValue);
      if (state.previousValue == null) {
        return {
          ...state,
          previousValue: inputValue,
          operation: action.operation,
          waitingForNewValue: true
        };
      }

      const currentValue = state.previousValue;
      let newValue = currentValue;

      switch (state.operation) {
        case '+':
          newValue = currentValue + inputValue;
          break;
        case '-':
          newValue = currentValue - inputValue;
          break;
        case '*':
          newValue = currentValue * inputValue;
          break;
        case '/':
          newValue = currentValue / inputValue;
          break;
        default:
          break;
      }

      return {
        ...state,
        displayValue: String(newValue),
        previousValue: newValue,
        operation: action.operation,
        waitingForNewValue: true
      };

    default:
      return state;
  }
}

// Create the Redux store
const store = createStore(calculatorReducer);

export default store;