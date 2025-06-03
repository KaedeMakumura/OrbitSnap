from pprint import pprint
from dataclasses import asdict, is_dataclass
import os

DEBUG = os.getenv("DEBUG", "0") == "1"

def pr(value, title=None):
    """開発用デバッグプリント"""
    # if not DEBUG:
    #     return
    if title:
        print(f"--- {title} ---")
    if is_dataclass(value):
        pprint(asdict(value))
    else:
        pprint(value)