from __future__ import absolute_import
# This file houses all default settings for the Crawler
# to override please use a custom localsettings.py file

# Scrapy Cluster Settings
# ~~~~~~~~~~~~~~~~~~~~~~~

# Specify the host, port and password to use when connecting to Redis.
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10

# Kafka server information
KAFKA_HOSTS = ['localhost:9092']
KAFKA_TOPIC_PREFIX = 'behoof'
KAFKA_APPID_TOPICS = True
# base64 encode the html body to avoid json dump errors due to malformed text
KAFKA_BASE_64_ENCODE = False
KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking
KAFKA_PRODUCER_MAX_REQUEST_SIZE = 1024 * 1024 # 1MB

ZOOKEEPER_ASSIGN_PATH = '/scrapy-cluster/crawler/'
ZOOKEEPER_ID = 'all'
ZOOKEEPER_HOSTS = 'localhost:2181'

PUBLIC_IP_URL = 'http://ip.42.pl/raw'
IP_ADDR_REGEX = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# seconds to wait between seeing new queues, cannot be faster than spider_idle time of 5
SCHEDULER_QUEUE_REFRESH = 10

# throttled queue defaults per domain, x hits in a y second window
QUEUE_HITS = 10
QUEUE_WINDOW = 60

# we want the queue to produce a consistent pop flow
QUEUE_MODERATED = True

# how long we want the duplicate timeout queues to stick around in seconds
DUPEFILTER_TIMEOUT = 600

# how many pages to crawl for an individual domain. Cluster wide hard limit.
GLOBAL_PAGE_PER_DOMAIN_LIMIT = None

# how long should the global page limit per domain stick around in seconds
GLOBAL_PAGE_PER_DOMAIN_LIMIT_TIMEOUT = 600

# how long should the individual domain's max page limit stick around in seconds
DOMAIN_MAX_PAGE_TIMEOUT = 600

# how often to refresh the ip address of the scheduler
SCHEDULER_IP_REFRESH = 60

# whether to add depth >= 1 blacklisted domain requests back to the queue
SCHEDULER_BACKLOG_BLACKLIST = True

'''
----------------------------------------
The below parameters configure how spiders throttle themselves across the cluster
All throttling is based on the TLD of the page you are requesting, plus any of the
following parameters:

Type: You have different spider types and want to limit how often a given type of
spider hits a domain

IP: Your crawlers are spread across different IP's, and you want each IP crawler clump
to throttle themselves for a given domain

Combinations for any given Top Level Domain:
None - all spider types and all crawler ips throttle themselves from one tld queue
Type only - all spiders throttle themselves based off of their own type-based tld queue,
    regardless of crawler ip address
IP only - all spiders throttle themselves based off of their public ip address, regardless
    of spider type
Type and IP - every spider's throttle queue is determined by the spider type AND the
    ip address, allowing the most fined grained control over the throttling mechanism
'''
# add Spider type to throttle mechanism
SCHEDULER_TYPE_ENABLED = True

# add ip address to throttle mechanism
SCHEDULER_IP_ENABLED = True
'''
----------------------------------------
'''

# how many times to retry getting an item from the queue before the spider is considered idle
SCHEUDLER_ITEM_RETRIES = 3

# how long to keep around stagnant domain queues
SCHEDULER_QUEUE_TIMEOUT = 3600

# log setup scrapy cluster crawler
SC_LOG_DIR = 'logs'
SC_LOG_MAX_BYTES = 10 * 1024 * 1024
SC_LOG_BACKUPS = 5
SC_LOG_STDOUT = True
SC_LOG_JSON = False
SC_LOG_LEVEL = 'INFO'

# stats setup
STATS_STATUS_CODES = True
STATS_RESPONSE_CODES = [
    200,
    404,
    403,
    504,
]
STATS_CYCLE = 5
# from time variables in scutils.stats_collector class
STATS_TIMES = [
    'SECONDS_15_MINUTE',
    'SECONDS_1_HOUR',
    'SECONDS_6_HOUR',
    'SECONDS_12_HOUR',
    'SECONDS_1_DAY',
    'SECONDS_1_WEEK',
]

BOT_NAME = 'holodilnik'

SPIDER_MODULES = ['holodilnik.spiders']
NEWSPIDER_MODULE = 'holodilnik.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True
TELNETCONSOLE_PORT = [6123]
TELNETCONSOLE_PASSWORD = 'yparcs'

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'ru-RU,ru;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': USER_AGENT
}

# Enables scheduling storing requests queue in redis.
SCHEDULER = "bhfutils.crawler.distributed_scheduler.DistributedScheduler"

# Store scraped item in redis for post-processing.
ITEM_PIPELINES = {
    'bhfutils.crawler.pipelines.KafkaPipeline': 100,
    'bhfutils.crawler.pipelines.LoggingBeforePipeline': 1,
}

SPIDER_MIDDLEWARES = {
    # disable built-in DepthMiddleware, since we do our own
    # depth management per crawl request
    'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
    'bhfutils.crawler.meta_passthrough_middleware.MetaPassthroughMiddleware': 100,
    'bhfutils.crawler.redis_stats_middleware.RedisStatsMiddleware': 101
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

DOWNLOAD_HANDLERS = {
    "https": "bhfutils.crawler.playwright.handler.ScrapyPlaywrightDownloadHandler",
}

DOWNLOADER_MIDDLEWARES = {
    # Handle timeout retries with the redis scheduler and logger
    'holodilnik.middlewares.HolodilnikDownloadMiddleware': 800,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'bhfutils.crawler.redis_retry_middleware.RedisRetryMiddleware': 510,
    # exceptions processed in reverse order
    'bhfutils.crawler.log_retry_middleware.LogRetryMiddleware': 520,
    'bhfutils.crawler.proxy_rotate.RotatingProxyMiddleware': 610,
    'bhfutils.crawler.proxy_rotate.BanDetectionMiddleware': 620,
    # custom cookies to not persist across crawl requests
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'bhfutils.crawler.custom_cookies.CustomCookiesMiddleware': 700,
}

# Disable the built in logging in production
LOG_ENABLED = True

# Allow all return codes
HTTPERROR_ALLOW_ALL = True

RETRY_TIMES = 3

ROTATING_PROXY_PAGE_RETRY_TIMES = 10
DOWNLOAD_TIMEOUT = 100

# Avoid in-memory DNS cache. See Advanced topics of docs for info
DNSCACHE_ENABLED = True

# Playwright
PLAYWRIGHT_BROWSER_TYPE = 'firefox'
PLAYWRIGHT_LAUNCH_OPTIONS = {
}
PLAYWRIGHT_STATIC_CONTEXT = {
    "extra_http_headers": {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'cache-control': 'max-age=0',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    },
    "locale": "ru-RU",
    "java_script_enabled": True
}
PLAYWRIGHT_DYNAMIC_CONTEXTS = [
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0"
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    }
]
PLAYWRIGHT_ABORT_REQUEST = lambda req: req.resource_type == "image"
PLAYWRIGHT_PROCESS_REQUEST_HEADERS = "bhfutils.crawler.playwright.headers.use_playwright_headers"

ROTATING_PROXY_LIST = ['https://w3e1vb:h3AYFJ@196.18.181.61:8000', 'https://w3e1vb:h3AYFJ@196.18.183.147:8000',
                       'https://w3e1vb:h3AYFJ@196.18.180.242:8000', 'https://w3e1vb:h3AYFJ@196.18.182.50:8000',
                       'https://w3e1vb:h3AYFJ@196.18.182.251:8000', 'https://w3e1vb:h3AYFJ@196.18.183.81:8000',
                       'https://w3e1vb:h3AYFJ@196.18.180.132:8000', 'https://w3e1vb:h3AYFJ@196.18.182.191:8000',
                       'https://w3e1vb:h3AYFJ@196.18.183.73:8000', 'https://w3e1vb:h3AYFJ@196.18.180.37:8000']
# ~~~~~~~~~~~~~~~ #
# Local Overrides #
# ~~~~~~~~~~~~~~~ #

try:
    from .localsettings import *
except ImportError:
    pass