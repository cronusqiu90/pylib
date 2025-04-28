# type: ignore
import functools
import os
import sys
import time

from loguru import logger as _slog, _file_sink
from loguru._datetime import aware_now
from loguru._logger import Logger, Core

__all__ = ("get_daily_logger", "get_default_logger", "set_level")

setattr(sys, "tracebacklimit", 2)
_default_log_format = (
    "{time:YYYY/MM/DD HH:mm:ss.SSS} | "
    "{level: <7} | "
    "{extra[mod]} | "
    "{module}:{line} | "
    "{message}"
)
_slog.remove()
_slog.add(sink=sys.stdout, level="INFO", format=_default_log_format, backtrace=True, colorize=False)
_slog = _slog.bind(mod="slog")


class _FileDateFormatter:
    def __init__(self, datetime=None):
        self.datetime = datetime or aware_now()

    def __format__(self, spec):
        return self.datetime.__format__("%Y-%m-%d_%H%M%S%f")


class _FileSink(_file_sink.FileSink):
    def _create_path(self):
        path = self._path.format_map({"time": _FileDateFormatter()})
        return os.path.abspath(path)

    def _terminate_file(self, *, is_rotating=False):
        if self._file is not None:
            self._close_file()

        if is_rotating:
            new_path = self._create_path()
            print("new_path=", new_path)
            self._create_dirs(new_path)
            self._create_file(new_path)


@functools.lru_cache()
def get_daily_logger(mod, name):
    path = os.path.join(os.getcwd(), "logs", name + "-{time}.log")
    _sink = _FileSink(path, rotation="00:00")
    _log = Logger(
        core=Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patchers=[],
        extra={"mod": mod},
    )
    _log.remove()
    _log.add(
        _sink,
        level="INFO",
        format=_default_log_format,
        backtrace=True,
        colorize=False
    )
    return _log


def get_default_logger():
    return _slog


def set_level(logger, level):
    _, no, _, _ = logger.level(level)
    _core = getattr(logger, "_core")
    with _core.lock:
        setattr(_core, "min_level", no)
        for handler in _core.handlers.values():
            handler._levelno = no
