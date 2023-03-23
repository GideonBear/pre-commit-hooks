import sys
from pathlib import Path

from pre_commit_meta_hooks import run


sys.exit(run(Path(__file__).parent))
