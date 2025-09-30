"""Shim to run CLI as `python -m zyra.cli.runner`.

Delegates to the top-level `cli.runner` module.
"""

from cli.runner import *  # re-export for compatibility

if __name__ == "__main__":
    from cli.runner import main

    main()
