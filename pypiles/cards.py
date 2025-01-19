from pypiles.colors import get_colors
from pypiles.items import get_items


class Card:
    def __init__(self, color: str, item: str) -> None:
        self.color = color
        self.item = item
        self.id = f"{color}::{item}"

    def __repr__(self) -> str:
        return f"[{self.id}]"


def create_card(color: str, item: str) -> Card:
    """Factory function for playing card object.
    Adds checks to ensure provided color and item are valid."""
    assert color in get_colors(), f"Color '{color}' is not a valid option."
    assert item in get_items(), f"Item '{item}' is not a valid option."
    return Card(color=color, item=item)
