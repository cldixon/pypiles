import random

import pytest

from pypiles.cards import Card
from pypiles.strategies.greedy import GreedySwapper


def make_card(color: str, item: str) -> Card:
    return Card(color=color, item=item)


class TestGreedySwapper:
    def setup_method(self):
        self.strategy = GreedySwapper()

    def test_returns_swap_request_or_none(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "cardigan"),
             make_card("green", "hoody"), make_card("yellow", "mittens")],
        ]
        center = [
            make_card("pink", "tophat"), make_card("orange", "cardigan"),
            make_card("purple", "hoody"), make_card("white", "mittens"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        assert "target" in result
        assert "swap" in result

    def test_state_1111_with_item_match_in_center(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "cardigan"),
             make_card("green", "hoody"), make_card("yellow", "mittens")],
        ]
        center = [
            make_card("pink", "tophat"), make_card("orange", "flip-flops"),
            make_card("purple", "sweat-pants"), make_card("white", "trenchcoat"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        # Target should be a card whose item matches something in the player pile
        assert result["target"][1].item in {"tophat", "cardigan", "hoody", "mittens"}

    def test_state_211_max_item_in_center(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "tophat"),
             make_card("green", "hoody"), make_card("yellow", "mittens")],
        ]
        center = [
            make_card("pink", "tophat"), make_card("orange", "flip-flops"),
            make_card("purple", "sweat-pants"), make_card("white", "trenchcoat"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        assert result["target"][1].item == "tophat"
        # Should send a minority card, not tophat
        assert result["swap"][2].item != "tophat"

    def test_state_211_fallback_no_match(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "tophat"),
             make_card("green", "hoody"), make_card("yellow", "mittens")],
        ]
        center = [
            make_card("pink", "flip-flops"), make_card("orange", "sweat-pants"),
            make_card("purple", "trenchcoat"), make_card("white", "cardigan"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        # Should send a minority card even without a match
        assert result["swap"][2].item != "tophat"

    def test_state_22_with_item_match(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "tophat"),
             make_card("green", "cardigan"), make_card("yellow", "cardigan")],
        ]
        center = [
            make_card("pink", "tophat"), make_card("orange", "flip-flops"),
            make_card("purple", "sweat-pants"), make_card("white", "trenchcoat"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        assert result["target"][1].item in {"tophat", "cardigan"}

    def test_state_31_max_item_in_center(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "tophat"),
             make_card("green", "tophat"), make_card("yellow", "mittens")],
        ]
        center = [
            make_card("pink", "tophat"), make_card("orange", "flip-flops"),
            make_card("purple", "sweat-pants"), make_card("white", "trenchcoat"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        assert result["target"][1].item == "tophat"
        assert result["swap"][2].item == "mittens"

    def test_state_31_fallback_no_match(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "tophat"),
             make_card("green", "tophat"), make_card("yellow", "mittens")],
        ]
        center = [
            make_card("pink", "flip-flops"), make_card("orange", "cardigan"),
            make_card("purple", "sweat-pants"), make_card("white", "trenchcoat"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        assert result["swap"][2].item == "mittens"

    def test_empty_player_cards_returns_none(self):
        center = [
            make_card("pink", "flip-flops"), make_card("orange", "cardigan"),
            make_card("purple", "sweat-pants"), make_card("white", "trenchcoat"),
        ]
        result = self.strategy.find_swap([], center)
        assert result is None

    def test_swap_indices_within_bounds(self):
        random.seed(42)
        player_cards = [
            [make_card("red", "tophat"), make_card("blue", "cardigan"),
             make_card("green", "hoody"), make_card("yellow", "mittens")],
            [make_card("pink", "flip-flops"), make_card("orange", "sweat-pants"),
             make_card("purple", "trenchcoat"), make_card("white", "cardigan")],
        ]
        center = [
            make_card("gray", "tophat"), make_card("black", "flip-flops"),
            make_card("red", "hoody"), make_card("blue", "sweat-pants"),
        ]
        result = self.strategy.find_swap(player_cards, center)
        assert result is not None
        pile_idx = result["swap"][0]
        card_idx = result["swap"][1]
        assert 0 <= pile_idx < len(player_cards)
        assert 0 <= card_idx < len(player_cards[pile_idx])
        target_pos = result["target"][0]
        assert 0 <= target_pos < len(center)
