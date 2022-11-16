import logging
import os

logger = logging.getLogger()
logging.basicConfig(format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s")
logger.setLevel(logging.INFO)

base_dir = os.path.dirname(os.path.realpath(__file__))
