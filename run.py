import sys
from pathlib import Path

import pre_commit_meta_hooks


sys.exit(pre_commit_meta_hooks.run(Path(__file__).parent))
