DEFAULT_NUM_ITEMS = 50

ITEMS = [
    "argyle-sweater-vest",
    "baseball-cap",
    "baseball-jersey",
    "basketball-jersey",
    "board-shorts",
    "cardigan",
    "cargo-pants",
    "cargo-shorts",
    "bath-robe",
    "dress-shirt",
    "flip-flops",
    "gym-shorts-female",
    "gym-shorts-male",
    "hoody",
    "hawaian-shirt",
    "high-top-socks",
    "khaki-pants",
    "jean-overalls",
    "leather-belt",
    "letterman-jacket",
    "long-sleeve-tee",
    "low-top-socks",
    "mittens",
    "one-piece-swimsuit",
    "pajama-pants",
    "plaid-buttondown",
    "puffy-jacket",
    "short-sleeve-polo",
    "short-sleeve-tee",
    "skinny-jeans",
    "sleeveless-blouse",
    "snow-boots",  # added to fill out deck
    "sports-bra",
    "straight-jeans",
    "striped-sleeveless-tee",
    "sun-dress",
    "sweat-pants",
    "swim-shorts",
    "tennis-shoes",
    "toboggan-hat",  # added to fill out deck
    "tophat",
    "trenchcoat",
    "trucker-jacket",
    "turtleneck-sweater",
    "two-piece-swimsuit",
    "wide-sleeved-blouse",
    "winter-beanie",
    "winter-scarf",
    "wool-socks",
    "zip-pullover",
]


def get_items(_expected_num_items: int = 50) -> list[str]:
    """Return list of playing card 'items' after performing quality control checks."""
    # the number of items in list above should be kept in correct state
    # due to how cards are distributed by number of players.
    assert (
        len(ITEMS) == _expected_num_items
    ), f"Default items list contains {len(ITEMS)}, but expected number is {_expected_num_items}."

    num_unique_items = len(set(ITEMS))
    assert (
        num_unique_items == len(ITEMS)
    ), f"Items list may contain a duplicate. List has {len(ITEMS)} items, but only {num_unique_items} are unique."
    return ITEMS
