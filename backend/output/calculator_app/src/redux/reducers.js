javascript
// src/redux/reducers.js

const initialState = {
  displayValue: '0',
  previousValue: null,
  operation: null,
  waitingForNewValue: false,
};

function calculatorReducer(state = initialState, action) {
  switch (action.type) {
    case 'INPUT_NUMBER':
      if (state.waitingForNewValue) {
        return {
          ...state,
          displayValue: action.payload,
          waitingForNewValue: false,
        };
      }
      return {
        ...state,
        displayValue: state.displayValue === '0' ? action.payload : state.displayValue + action.payload,
      };

    case 'INPUT_DECIMAL':
      if (state.waitingForNewValue) {
        return {
          ...state,
          displayValue: '0.',
          waitingForNewValue: false,
        };
      }
      if (!state.displayValue.includes('.')) {
        return {
          ...state,
          displayValue: state.displayValue + '.',
        };
      }
      return state;

    case 'CLEAR':
      return initialState;

    case 'SET_OPERATION':
      if (state.operation && state.waitingForNewValue) {
        return {
          ...state,
          operation: action.payload,
        };
      }
      if (state.previousValue == null) {
        return {
          ...state,
          previousValue: state.displayValue,
          operation: action.payload,
          waitingForNewValue: true,
        };
      }
      return {
        ...state,
        previousValue: calculate(state),
        operation: action.payload,
        waitingForNewValue: true,
      };

    case 'EVALUATE':
      if (state.operation == null || state.waitingForNewValue) {
        return state;
      }
      return {
        ...state,
        displayValue: calculate(state),
        previousValue: null,
        operation: null,
        waitingForNewValue: false,
      };

    default:
      return state;
  }
}

function calculate({ previousValue, displayValue, operation }) {
  const prev = parseFloat(previousValue);
  const current = parseFloat(displayValue);
  if (isNaN(prev) || isNaN(current)) return displayValue;

  let result;
  switch (operation) {
    case '+':
      result = prev + current;
      break;
    case '-':
      result = prev - current;
      break;
    case '*':
      result = prev * current;
      break;
    case '/':
      result = current !== 0 ? prev / current : 'Error';
      break;
    default:
      return displayValue;
  }
  return result.toString();
}

export default calculatorReducer;