from datetime import datetime


def now() -> int:
    return int(datetime.now().timestamp())
