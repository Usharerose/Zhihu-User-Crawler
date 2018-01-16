import zhihu_crawler, zhihu_bloom
import time, queue, os, threading

crawler = zhihu_crawler.Zhihu_Crawler()
bf = zhihu_bloom.BloomFilter()

def starter(inputurl, queue):
    if not bf.contains(inputurl):
        bf.add(inputurl)
        url_list = crawler.parse_user_profile(url=inputurl)
        for x in url_list:
            queue.put(x)
        print('ok')
    else:
        print('This has exited, which will be ignored')

def worker(queue):
    while True:
        url = queue.get()
        url_list = crawler.parse_user_profile(url=url)
        for x in url_list:
            if not bf.contains(x):
                queue.put(x)
                bf.add(x)
            else:
                print('This has exited, which will be ignored')
        print('ok')

if __name__ == "__main__":

    # the start page
    q = queue.Queue()
    initial_url = 'https://www.zhihu.com/people/sgai'
    starter(initial_url, q)

    for x in range(os.cpu_count()*3):
        task = threading.Thread(target=worker, args=(q,))
        task.setDaemon(True)
        task.start()

    q.join()
