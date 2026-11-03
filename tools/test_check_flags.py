from check_flags import ending_for

def test_all_true_is_a():
    assert ending_for(True, True, True) == "a"

def test_two_true_is_a():
    assert ending_for(True, True, False) == "a"
    assert ending_for(True, False, True) == "a"
    assert ending_for(False, True, True) == "a"

def test_one_or_zero_is_b():
    assert ending_for(True, False, False) == "b"
    assert ending_for(False, False, False) == "b"
