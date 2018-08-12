#!/usr/bin/env python3
"""Basic Bot that recognises simple commands

The Google Assistant Library can be installed with:
    pip install -r requirements.txt

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

from json import load

from src import Butler

if __name__ == "__main__":
    with open("./config.json") as data:
        Butler(load(data)).start()
