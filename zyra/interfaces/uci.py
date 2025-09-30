"""Shim to run UCI module as `python -m zyra.interfaces.uci`.

Delegates to the top-level `interfaces.uci` module so we don't duplicate code.
"""

from interfaces.uci import *  # re-export for compatibility

if __name__ == "__main__":
    from interfaces.uci import main

    main()
