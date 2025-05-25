import os
import tempfile
from collections.abc import Iterable
from contextlib import contextmanager


@contextmanager
def temporary_files(files: Iterable[tuple[str, bytes]], prefix: str = "tmp_"):
    paths = []

    try:
        for i, (suffix, content) in enumerate(files):
            if content is None:
                continue
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=f"{prefix}{i}_")
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(content)
            paths.append(path)

        yield paths

    finally:
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
