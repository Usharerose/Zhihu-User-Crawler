import re, queue, threading, requests, fake_useragent
from mongoengine import NotUniqueError
from lxml import html
from zhihu_db import Proxy
from zhihu_config import PROXY_REGU, PROXY_SITES_LIST, TIMEOUT

def visit_func(url, proxy=None):
    s = requests.session()
    s.headers.update({'User-Agent': fake_useragent.UserAgent().random})
    proxies = None
    if proxy is not None:
        proxies = {
            'http': proxy
        }
    return s.get(url, timeout=TIMEOUT, proxies=proxies)

def save_proxies(url):
    proxies = []
    try:
        r = visit_func(url)
    except requests.exceptions.RequestException:
        return False

    #解析'http://www.proxylists.net/?HTTP'
    addresses = re.findall(PROXY_REGU, r.text)

    if len(addresses) == 0:
        tree = html.fromstring(r.content)

        #解析https://www.kuaidaili.com/free/inha'
        el = tree.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
        if len(el) == 0:
            #解析'http://www.proxylists.net/?HTTP'
            el2 = tree.xpath('//table[@id="ip_list"]/tr')
            el2.pop(0)
            for ele in el2:
                IP1 = ele.xpath('td[2]/text()')[0] + ':' + ele.xpath('td[3]/text()')[0]
                addresses.append(IP1)

        else:
            for ele in el:
                IP = ele.xpath('td[@data-title="IP"]/text()')[0] + ':' + ele.xpath('td[@data-title="PORT"]/text()')[0]
                addresses.append(IP)


    for address in addresses:
        proxy = Proxy(
            address=address
        )
        try:
            proxy.save()
        except NotUniqueError:
            pass
        else:
            proxies.append(address)

    return proxies

def cleanup():
    Proxy.drop_collection()

def save_proxies_with_queue2(in_queue, out_queue):
    while True:
        url = in_queue.get()
        rs = save_proxies(url)
        out_queue.put(rs)
        in_queue.task_done()  # 队列完成发送信号


def append_result(out_queue, result):
    while True:
        rs = out_queue.get()
        if rs:
            result.extend(rs)
        out_queue.task_done()

def use_thread_with_queue2():
    cleanup()
    in_queue = queue.Queue()
    out_queue = queue.Queue()

    for i in range(3):
        t = threading.Thread(target=save_proxies_with_queue2,
                             args=(in_queue, out_queue))
        t.setDaemon(True)
        t.start()

    for url in PROXY_SITES_LIST:
        in_queue.put(url)

    result = []

    for i in range(5):
        t = threading.Thread(target=append_result,
                             args=(out_queue, result))
        t.setDaemon(True)
        t.start()

    in_queue.join()
    out_queue.join()

    print(len(result))
    return result

proxy_list = use_thread_with_queue2()
