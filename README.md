# Zhihu-User-Crawler
Crawling Zhihu users' Info based on users' following list
## Requirements
requests and http.cookiejar,<br>
lxml and json,<br>
mongoengine(MongoDB),<br>
PIL,<br>
mmh3 and bitarray
## Process
1) Using Zhihu account to sign in, saving the cookies.<br>
2) Using Xpath and re to parse the html, getting one user's basic information.<br>
3) Using threading(multiprocessing.dummy) to crawl one user's following list.<br>
4) Using Queue to save the urls, crawling the urls concurrently.<br>
5) Using BloomFilter for testing urls' membership in a set.
6) Adding proxy crawler, getting proxy url for requesting.
