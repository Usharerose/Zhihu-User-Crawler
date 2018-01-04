# Zhihu-User-Crawler
Crawling Zhihu users' Info based on users' following list
# Requirements
requests, mongoengine(MongoDB), lxml, queue, multiprocessing.dummy, lock
# Process
1）Using Zhihu account to sign in, saving the cookies.
2) Using Xpath to parse the html, getting one user's basic information.
3) Using threading(multiprocessing.dummy) to crawl one user's following list.
4) Using Queue to save the urls, crawling the urls concurrently.
