#!/usr/bin/env python

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def main() -> int:
    config = Path(__file__).parent / sys.argv[1]
    params = sys.argv[2].split(' ')
    params = [] if params == [''] else params
    files = sys.argv[3:]

    config = prepare_config(config, params)

    retval = subprocess.call(
        # TODO: only `--color always` when color is on for this process? isatty?
        ['pre-commit', 'run', '--color', 'always', '--config', config, '--files'] + files
    )

    config.unlink()

    return retval


def prepare_config(config: Path, params: list[str]) -> Path:
    content = config.read_text(encoding='utf-8')

    new_content = content.replace('$HERE', str(config.parent.absolute()))
    for param in params:
        param, value = param.split('=')
        new_content = new_content.replace(f'${param}', value)

    new = get_tempfile('.pre-commit-config.yaml')
    new.write_text(new_content, encoding='utf-8')

    return new


def get_tempfile(suffix: str = None) -> Path:
    tempfile = NamedTemporaryFile(suffix=suffix, delete=False)
    return Path(tempfile.name)


if __name__ == '__main__':
    main()
