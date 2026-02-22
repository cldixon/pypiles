import pytest

from pypiles.cards import Card
from pypiles.logic import (
    cards_are_identical,
    cards_have_matching_item,
    center_pile_in_valid_state,
)


class TestCardsAreIdentical:
    def test_identical_cards(self):
        a = Card(color="red", item="tophat")
        b = Card(color="red", item="tophat")
        assert cards_are_identical(a, b) is True

    def test_different_color_same_item(self):
        a = Card(color="red", item="tophat")
        b = Card(color="blue", item="tophat")
        assert cards_are_identical(a, b) is False

    def test_same_color_different_item(self):
        a = Card(color="red", item="tophat")
        b = Card(color="red", item="cardigan")
        assert cards_are_identical(a, b) is False

    def test_completely_different(self):
        a = Card(color="red", item="tophat")
        b = Card(color="blue", item="cardigan")
        assert cards_are_identical(a, b) is False


class TestCardsHaveMatchingItem:
    def test_matching_item_different_color(self):
        a = Card(color="red", item="tophat")
        b = Card(color="blue", item="tophat")
        assert cards_have_matching_item(a, b) is True

    def test_different_items(self):
        a = Card(color="red", item="tophat")
        b = Card(color="blue", item="cardigan")
        assert cards_have_matching_item(a, b) is False

    def test_identical_cards_raises(self):
        a = Card(color="red", item="tophat")
        b = Card(color="red", item="tophat")
        with pytest.raises(AssertionError):
            cards_have_matching_item(a, b)


class TestCenterPileInValidState:
    def test_all_unique_cards(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="cardigan"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        assert center_pile_in_valid_state(cards) is True

    def test_duplicate_card(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="red", item="tophat"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        assert center_pile_in_valid_state(cards) is False

    def test_same_item_different_colors_is_valid(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        assert center_pile_in_valid_state(cards) is True
