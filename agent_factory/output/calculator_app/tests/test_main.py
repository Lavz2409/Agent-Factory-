import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from Calculator import calculateResult

def test_calculate_result_addition():
    result = calculateResult("2 + 2")
    assert result == 4

def test_calculate_result_subtraction():
    result = calculateResult("5 - 3")
    assert result == 2

def test_calculate_result_multiplication():
    result = calculateResult("3 * 4")
    assert result == 12

def test_calculate_result_division():
    result = calculateResult("8 / 2")
    assert result == 4

def test_calculate_result_complex_expression():
    result = calculateResult("2 + 3 * 4 - 5")
    assert result == 9

def test_calculate_result_invalid_expression():
    with pytest.raises(Exception):
        calculateResult("2 + ")

def test_calculate_result_empty_expression():
    with pytest.raises(Exception):
        calculateResult("")