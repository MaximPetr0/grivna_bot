from datetime import datetime
from zoneinfo import ZoneInfo

KYIV = ZoneInfo("Europe/Kyiv")


def now_kyiv():
    return datetime.now(KYIV).replace(tzinfo=None)



