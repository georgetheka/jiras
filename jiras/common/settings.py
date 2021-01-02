import os
import sys
from dataclasses import dataclass
from typing import Callable, Union


def _arg(index: int) -> str:
    assert len(sys.argv) > index, f'Argument with index {index} not found'
    return sys.argv[index]


def _env(key: str) -> str:
    v = os.getenv(key)
    assert v, f'Env variable {key} is not set or empty'
    return v


class DeferredString:
    def __init__(self, fn: Callable, key_or_arg: Union[int, str]):
        self._fn = fn
        self._key_or_arg = key_or_arg

    def resolve(self) -> str:
        return self._fn(self._key_or_arg)


def from_env(key: str) -> DeferredString:
    return DeferredString(fn=_env, key_or_arg=key)


def from_arg(arg_index: int) -> DeferredString:
    return DeferredString(fn=_arg, key_or_arg=arg_index)


def make_settings() -> 'Settings':
    s = Settings()
    for field in s.__dict__:
        attr = getattr(s, field)
        if isinstance(attr, DeferredString):
            setattr(s, field, attr.resolve())
    return s


# -----------------------------------------------------------------
# ------ Configure your runtime below ------------------------------

@dataclass
class Settings:
    db_host: str = 'localhost'
    db_port: int = 5432
    db_database: str = 'jiras'
    db_user: str = 'jiras'
    db_pass: str = 'jiras'
    jira_server: Union[str, DeferredString] = from_arg(1)
    jira_query: Union[str, DeferredString] = from_arg(2)
    jira_query_limit: Union[str, DeferredString] = from_arg(3)
    jira_user: Union[str, DeferredString] = from_env('JIRA_USER')
    jira_pass: Union[str, DeferredString] = from_env('JIRA_PASS')
    pickle_filepath: str = './data/jiras.bin'

# -----------------------------------------------------------------
