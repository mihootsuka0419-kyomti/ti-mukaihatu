import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "excuses.json"
)


def load_excuse_data():
    with DATA_FILE.open(
        mode="r",
        encoding="utf-8"
    ) as file:
        return json.load(file)