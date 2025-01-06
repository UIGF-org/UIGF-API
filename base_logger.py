import logging
import os


logger = logging
if os.getenv("DEBUG") == "1":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s %(asctime)s -> %(message)s',

        datefmt='%Y-%m-%dT%H:%M:%S')
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(asctime)s -> %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
