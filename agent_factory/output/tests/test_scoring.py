```
import pytest
from rules.scoring import calculate_score

@pytest.mark.parametrize("ats_results, expected_score", [
    ({"keywords": True, "sections": True, "formatting": True}, 100),
    ({"keywords": True, "sections": True, "formatting": False}, 80),
    ({"keywords": True, "sections": False, "formatting": True}, 70),
    ({"keywords": False, "sections": True, "formatting": True}, 60),
    ({"keywords": True, "sections": False, "formatting": False}, 50),
    ({"keywords": False, "sections": True, "formatting": False}, 40),
    ({"keywords": False, "sections": False, "formatting": True}, 30),
    ({"keywords": False, "sections": False, "formatting": False}, 0),
])
def test_calculate_score(ats_results, expected_score):
    score = calculate_score(ats_results)
    assert score == expected_score
```