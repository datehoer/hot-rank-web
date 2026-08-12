import json
import logging
import traceback

import aiohttp
from json_repair import repair_json
from config import news_sites
from hotrank.cache import redis_cache
