import zhihu_crawler, zhihu_bloomfilter
import time, queue, os
from multiprocessing.dummy import Pool

q = queue.Queue()
crawler = zhihu_crawler.Zhihu_Crawler()
bf = zhihu_bloomfilter.BloomFilter()

def starter(inputurl):
    url_list = crawler.parse_user_profile(url=inputurl)
    for x in url_list:
        q.put(x)
    print('ok')

def worker():
    while True:
        url = q.get()
        url_list = crawler.parse_user_profile(url=url)
        for x in url_list:
            if not bf.contain(x):
                q.put(x)
                bf.add(x)
            else:
                print('%s has existed, which will be ignored.' %x)

if __name__ == "__main__":
    initial_url = '请在这里输入您的爬取种子网页，如https://www.zhihu.com/people/XXXX'
    bf.add(initial_url)
    starter(initial_url)
    pool = Pool(os.cpu_count())
    task = pool.apply_async(func=worker)
    pool.close()
    pool.join()