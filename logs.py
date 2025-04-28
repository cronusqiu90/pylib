import sys
import functools
from loguru import logger as _logger
from loguru._logger import Core as _Core
from loguru._logger import Logger as _Logger

__all__ = ["getLogger", "init", "setLevel"]

sys.tracebacklimit = 2
_default_log_format = (
    "{time:YYYY/MM/DD HH:mm:ss.SSS} - "
    "[{level:>7}] - "
    "pid:{process.id} - "
    "{module}:{function}:{line:03d} - "
    "{message}"
)
_logger.remove()
_logger.add(sink=sys.stdout, level="INFO", format=_default_log_format, backtrace=True)


def init():
    _logger.remove()
    _logger.add(sink=sys.stdout, level="INFO", format=_default_log_format, backtrace=True)


@functools.lru_cache()
def getLogger(sink, level):
    logger = _Logger(
        core=_Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patcher=[],
        extra={},
    )
    logger.remove()
    logger.add(sink=sink, level=level, format=_default_log_format, backtrace=True)
    return logger


def setLevel(logger, new_level):
    _, nu, _, _ = logger.level(new_level)
    _core = getattr(logger, "_core")
    with _core.lock:
        setattr(_core, "min_level", nu)
        for handler in _core.handlers.values():
            handler._levelno = nu
