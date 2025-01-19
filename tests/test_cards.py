import pytest

from pypiles.cards import Card, create_card
from pypiles.colors import get_colors
from pypiles.items import get_items

VALID_COLOR = "black"
VALID_ITEM = "tophat"

INVALID_COLOR = "rainbow"
INVALID_ITEM = "cloak"


def test_create_card():
    """Test card creation factory function. Checks that provided colors and items are valid."""

    # create a valid card ('black::tophat')
    valid_card = create_card(color=VALID_COLOR, item=VALID_ITEM)
    assert valid_card
    assert isinstance(valid_card, Card)

    # create an invalid card (invalid color)
    with pytest.raises(AssertionError):
        assert create_card(color=INVALID_COLOR, item=VALID_ITEM)

    # create an invalid card (invalid item)
    with pytest.raises(AssertionError):
        assert create_card(color=VALID_COLOR, item=INVALID_ITEM)


def test_colors():
    assert get_colors()


def test_items():
    assert get_items()
