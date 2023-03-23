#!/usr/bin/env python

import subprocess
import sys
from pathlib import Path


def main() -> int:
    print('Args:', sys.argv)
    config = Path(__file__) / sys.argv[1]
    files = sys.argv[2:]

    prepare_config(config)

    return subprocess.call(
        # TODO: only `--color always` when color is on for this process? isatty?
        ['pre-commit', 'run', '--color', 'always', '--config', config, '--files'] + files
    )


def prepare_config(config: Path) -> None:
    content = config.read_text(encoding='utf-8')
    new_content = content.replace('$HERE', str(config.parent.absolute()))
    if content != new_content:
        config.write_text(new_content, encoding='utf-8')


if __name__ == '__main__':
    main()
