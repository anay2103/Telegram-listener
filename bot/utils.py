import json
from typing import Any

import fleep


def decode_json(data: bytes) -> Any:
    try:
        json_data = data.decode().replace("'", '"')
        data = json.loads(json_data)
    except Exception as exc:
        print(exc)
        return None
    return data


async def check_extension(data: bytes, extension: str = 'pdf') -> None:
    info = fleep.get(data)
    return info.extension_matches(extension)
