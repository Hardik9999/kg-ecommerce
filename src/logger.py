import sys
import logging

# Ensure UTF-8 with fallback replacement on Windows cp1252 / cmd / PowerShell console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class FlushingStreamHandler(logging.StreamHandler):
    """A StreamHandler that immediately flushes output after every record to ensure logs appear in real time."""
    def emit(self, record):
        try:
            super().emit(record)
            self.flush()
        except Exception:
            self.handleError(record)

_handler = FlushingStreamHandler(sys.stdout)
_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
_handler.setFormatter(_formatter)
_handler.setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with real-time stdout flushing and independent propagation.
    
    Guarantees immediate visibility across Uvicorn (FastAPI), CLI scripts, and background
    runners without being suppressed by third-party loggers or Windows cp1252 encodings.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if _handler not in logger.handlers:
        logger.handlers = [_handler]
    logger.propagate = False
    return logger
