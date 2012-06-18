# Need an __init__, so I thought I'd put the logger here

import logging
logger = logging.getLogger('cluster')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
