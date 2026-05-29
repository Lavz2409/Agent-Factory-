import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.redux.actions import addDigit, performOperation
from src.redux.reducers import calculatorReducer

def test_add_digit():
    digit = '5'
    expected_action = {
        'type': 'ADD_DIGIT',
        'digit': digit
    }
    action = addDigit(digit)
    assert action == expected_action

def test_perform_operation():
    operation = 'ADD'
    expected_action = {
        'type': 'PERFORM_OPERATION',
        'operation': operation
    }
    action = performOperation(operation)
    assert action == expected_action

def test_calculator_reducer_initial_state():
    initial_state = {
        'input': '',
        'result': 0
    }
    action = {}
    new_state = calculatorReducer(initial_state, action)
    assert new_state == initial_state

def test_calculator_reducer_add_digit():
    initial_state = {
        'input': '',
        'result': 0
    }
    action = addDigit('5')
    new_state = calculatorReducer(initial_state, action)
    assert new_state['input'] == '5'
    assert new_state['result'] == 0

def test_calculator_reducer_perform_operation():
    initial_state = {
        'input': '5',
        'result': 0
    }
    action = performOperation('ADD')
    new_state = calculatorReducer(initial_state, action)
    # Assuming the operation adds to the result
    assert new_state['result'] == 5  # This would depend on your implementation