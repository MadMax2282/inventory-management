import pytest

from src.utils.id_generator import IdGenerator
from src.utils.validators import (
    require_integer,
    require_non_empty,
    require_non_negative,
    require_positive,
)
from src.utils.exceptions import ValidationError


def test_require_positive_ok():
    assert require_positive(5, "x") == 5


def test_require_positive_zero_raises():
    with pytest.raises(ValidationError):
        require_positive(0, "x")


def test_require_positive_none_raises():
    with pytest.raises(ValidationError):
        require_positive(None, "x")


def test_require_positive_negative_raises():
    with pytest.raises(ValidationError):
        require_positive(-1, "x")


def test_require_non_negative_zero_ok():
    assert require_non_negative(0, "x") == 0


def test_require_non_negative_negative_raises():
    with pytest.raises(ValidationError):
        require_non_negative(-1, "x")


def test_require_non_negative_none_raises():
    with pytest.raises(ValidationError):
        require_non_negative(None, "x")


def test_require_non_empty_ok():
    assert require_non_empty("text", "x") == "text"


def test_require_non_empty_blank_raises():
    with pytest.raises(ValidationError):
        require_non_empty("   ", "x")


def test_require_non_empty_none_raises():
    with pytest.raises(ValidationError):
        require_non_empty(None, "x")


def test_require_integer_ok():
    assert require_integer(7, "x") == 7


def test_require_integer_float_raises():
    with pytest.raises(ValidationError):
        require_integer(7.5, "x")


def test_require_integer_bool_raises():
    with pytest.raises(ValidationError):
        require_integer(True, "x")


def test_id_generator_sequence():
    gen = IdGenerator("ABC")
    assert gen.next_id() == "ABC-00001"
    assert gen.next_id() == "ABC-00002"


def test_id_generator_reset():
    gen = IdGenerator("X")
    gen.next_id()
    gen.next_id()
    gen.reset()
    assert gen.next_id() == "X-00001"


def test_id_generator_unique_values():
    gen = IdGenerator("U")
    ids = {gen.next_id() for _ in range(50)}
    assert len(ids) == 50
