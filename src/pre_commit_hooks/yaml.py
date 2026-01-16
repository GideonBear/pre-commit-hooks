from __future__ import annotations

from ruamel.yaml import YAML


yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
