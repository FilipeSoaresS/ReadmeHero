def change_level(current, delta):
    target = current + delta
    if target < 1 or target > 6:
        return current
    return target


def test_left_decreases_heading_level():
    assert change_level(6, -1) == 5
    assert change_level(2, -1) == 1
    assert change_level(1, -1) == 1


def test_right_increases_heading_level():
    assert change_level(1, 1) == 2
    assert change_level(5, 1) == 6
    assert change_level(6, 1) == 6
