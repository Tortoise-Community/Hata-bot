import json
from typing import Dict, Union

with open("config.json") as fp:
    config = json.load(fp)

class Auth:
    DATABASE_SECRETS: Dict[str, Union[str, int]] = config.get("DATABASE")
