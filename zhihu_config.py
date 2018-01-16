import re

PROXY_SITES_LIST = [
    'http://www.xicidaili.com/nn/',
    'https://www.kuaidaili.com/free/inha',
    'http://www.proxylists.net/?HTTP',
    #'https://proxy.mimvp.com/free.php?proxy=in_hp' 端口号以图片展示
]

PROXY_REGU = re.compile(pattern='[0-9]+(?:\.[0-9]+){3}:\d{2,4}')

TIMEOUT = 5
