from contextlib import suppress
from pathlib import Path
from typing import List, Callable
from django.conf import settings
from django.db import connection
from django.test.utils import CaptureQueriesContext


def get_fixtures_list() -> List[str]:
    base_dir: Path = settings.BASE_DIR
    fixtures_dir = base_dir / "fixtures"

    return [fixture_path.resolve().absolute().as_posix() for fixture_path in fixtures_dir.iterdir()]


def echo_sql(func) -> Callable:
    def wrap(*args, **kwargs) -> None:
        with CaptureQueriesContext(connection) as ctx:
            with suppress(AssertionError):
                func(*args, **kwargs)

            for item in ctx.captured_queries:
                print(item, end="\n\n")
        return

    return wrap
