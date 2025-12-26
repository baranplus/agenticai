import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOG_FILE = REPO_ROOT / "app.log"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S %Z',
    handlers=[
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=10*1024*1024,
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
