from pypiles.cards import Card
from pypiles.scoring import group_cards_by_item, get_pile_status


class TestGroupCardsByItem:
    def test_all_unique_items(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="cardigan"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        groups = group_cards_by_item(cards)
        assert len(groups) == 4
        assert all(len(v) == 1 for v in groups.values())

    def test_two_pairs(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="cardigan"),
            Card(color="yellow", item="cardigan"),
        ]
        groups = group_cards_by_item(cards)
        assert len(groups) == 2
        assert len(groups["tophat"]) == 2
        assert len(groups["cardigan"]) == 2

    def test_all_same_item(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="tophat"),
            Card(color="yellow", item="tophat"),
        ]
        groups = group_cards_by_item(cards)
        assert len(groups) == 1
        assert len(groups["tophat"]) == 4

    def test_preserves_index_and_card(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="cardigan"),
            Card(color="green", item="tophat"),
        ]
        groups = group_cards_by_item(cards)
        tophat_entries = groups["tophat"]
        assert tophat_entries[0][0] == 0
        assert tophat_entries[1][0] == 2
        assert tophat_entries[0][1].color == "red"
        assert tophat_entries[1][1].color == "green"


class TestGetPileStatus:
    def test_state_1111(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="cardigan"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        status = get_pile_status(cards)
        assert status["state"] == "1-1-1-1"
        assert status["max_count"] == 1
        assert status["max_item"] is None
        assert status["complete"] is False

    def test_state_211(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        status = get_pile_status(cards)
        assert status["state"] == "2-1-1"
        assert status["max_count"] == 2
        assert status["max_item"] == "tophat"
        assert status["complete"] is False

    def test_state_22(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="cardigan"),
            Card(color="yellow", item="cardigan"),
        ]
        status = get_pile_status(cards)
        assert status["state"] == "2-2"
        assert status["max_count"] == 2
        assert isinstance(status["max_item"], list)
        assert len(status["max_item"]) == 2
        assert status["complete"] is False

    def test_state_31(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="tophat"),
            Card(color="yellow", item="cardigan"),
        ]
        status = get_pile_status(cards)
        assert status["state"] == "3-1"
        assert status["max_count"] == 3
        assert status["max_item"] == "tophat"
        assert status["complete"] is False

    def test_state_4star(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="tophat"),
            Card(color="yellow", item="tophat"),
        ]
        status = get_pile_status(cards)
        assert status["state"] == "4*"
        assert status["max_count"] == 4
        assert status["max_item"] == "tophat"
        assert status["complete"] is True

    def test_items_set(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="cardigan"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        status = get_pile_status(cards)
        assert status["items"] == {"tophat", "cardigan", "hoody", "mittens"}

    def test_groups_populated(self):
        cards = [
            Card(color="red", item="tophat"),
            Card(color="blue", item="tophat"),
            Card(color="green", item="hoody"),
            Card(color="yellow", item="mittens"),
        ]
        status = get_pile_status(cards)
        assert "tophat" in status["groups"]
        assert len(status["groups"]["tophat"]) == 2
