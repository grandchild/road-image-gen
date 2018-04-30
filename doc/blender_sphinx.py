#!/usr/bin/env python3
import sys
from sphinx.cmd import build

first_sphinx_arg = sys.argv.index('-M')
# print(sys.argv[first_sphinx_arg:])
build.make_main(sys.argv[first_sphinx_arg:])
