#!/usr/bin/env python3
"""A startup file for the tickets_plus bot

We don't really do anything except invoke the start_bot function.
All the magic happens in tickets_plus.__init__.py
This file is to be used as a script, not as a module.

Example:
    $ python3 start_bot.py
"""
# License: EPL 2.0
import asyncio
import sys

import tickets_plus

def main():
    if (sys.platform == "win32"
       ):  # Psycopg3 doesn't work on Windows in async mode without this
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tickets_plus.start_bot())

if __name__ == "__main__":
    main()
