from pathlib import Path

import pre_commit_meta_hooks


def run() -> int:
    return pre_commit_meta_hooks.run(Path(__file__).parent)
