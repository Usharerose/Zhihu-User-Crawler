import requests, json, re, time, os, random
from lxml import html
import zhihu_cookie, zhihu_db
from zhihu_proxy import proxy_list
from multiprocessing.dummy import Pool
from threading import Lock

class Zhihu_Crawler(object):
    def __init__(self):
        #要保证所有的请求动作由同一个opener（self.s）执行
        self.cookie_get = zhihu_cookie.Zhihu_Cookie()
    
    #获取用户关注的人主页的响应内容
    def send_request(self, url):
        self.cookie_get.login_execute()
        #用户“关注的人”的url
        added_following_url = url + '/followees'
        r = self.cookie_get.s.get(added_following_url, headers=self.cookie_get.headers, verify=False, proxies={'http':'http://'+random.choice(proxy_list)})
        self.cookies = self.cookie_get.s.cookies
        self.headers = self.cookie_get.headers
        return r.content

    def parse_content_return(self, source):
        if source:
            return source[0]
        else:
            return ''
    
    #获得用户的Hash ID，用于后续操作
    def get_hashid(self, html_tree):
        hash_id_text = html_tree.xpath('//div[@class="zm-profile-header-op-btns clearfix"]/button/@data-id')
        return hash_id_text[0]
    
    #利用API，获取关注的人列表，单个列表中最多20条信息
    def get_followees(self, offset_num):
        refer_url = self.main_url
        hash_id  = self.user_hashid
        input_headers = self.headers
        input_cookies = self.cookies
        request_url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'
        params = {
            'offset' : offset_num,
            'order_by' : 'created',
            'hash_id' : hash_id
        }
        encode_params = json.dumps(params)
        headers = input_headers
        headers['Referer'] = refer_url
        cookies = input_cookies
        xsrf_value = cookies._cookies['www.zhihu.com']['/']['_xsrf'].value
        form_data = {
            'method': 'next',
            'params': encode_params,
            #'_xsrf': xsrf_value
        }
        headers['X-Xsrftoken'] = xsrf_value
        r = self.cookie_get.s.post(request_url, headers=headers, data=form_data, proxies={'http':'http://'+random.choice(proxy_list)})
        while r.status_code != 200:
            time.sleep(4)
            r = self.cookie_get.s.post(request_url, headers=headers, data=form_data, proxies={'http':'http://'+random.choice(proxy_list)})
        print(r.status_code)
        json_data = json.loads(r.content)
        followees_url = []
        for x in json_data['msg']:
            pattern = re.compile(r'href="/(people|org)/.+/answers"')
            url_token = re.search(pattern=pattern, string=x)
            url_token = url_token.group().replace('/answers"', '')
            url_token = url_token.replace('href="', '')
            url_token = 'https://www.zhihu.com' + url_token
            followees_url.append(url_token)
        return followees_url
    
    #解析用户信息
    def parse_user_profile(self, url):
        #用户信息初始化设置
        self.user_name = ''
        self.user_gender = ''
        self.user_location = ''
        self.user_education_school = ''
        self.user_education_subject = ''
        self.user_employment = ''
        self.user_employment_extra = ''
        self.user_following_num = ''
        self.user_follower_num = ''
        self.user_be_agreed_num = ''
        self.user_be_thanked_num = ''
        self.user_info = ''
        self.user_introduction = ''
        self.main_url = url

        html_source = self.send_request(self.main_url)
        tree = html.fromstring(html_source)

        #解析网页内容
        self.user_name = self.parse_content_return(tree.xpath('//a[@class="name"]/text()'))
        self.user_gender = self.parse_content_return(tree.xpath('//span[@class="item gender"]/i/@class'))
        if "female" in self.user_gender:
            self.user_gender = "female"
        else:
            if "male" in self.user_gender:
                self.user_gender = "male"
            else:
                self.user_gender = ""
        self.user_location = self.parse_content_return(tree.xpath('//span[@class="location item"]/a/text()'))
        self.user_education_school = self.parse_content_return(tree.xpath('span[@class="employment item"]/a/text()'))
        self.user_education_subject = self.parse_content_return(tree.xpath('//span[@class="education-extra item"]/a/text()'))
        self.user_employment = self.parse_content_return(tree.xpath('span[@class="employment item"]/a/text()'))
        self.user_employment_extra = self.parse_content_return(tree.xpath('span[@class="position item"]/a/text()'))
        self.user_following_num = self.parse_content_return(tree.xpath('//div[@class="zm-profile-side-following zg-clear"]/a[1]/strong/text()'))
        self.user_follower_num = self.parse_content_return(tree.xpath('//div[@class="zm-profile-side-following zg-clear"]/a[2]/strong/text()'))
        self.user_be_agreed_num = self.parse_content_return(tree.xpath('//span[@class="zm-profile-header-user-agree"]/strong/text()'))
        self.user_be_thanked_num = self.parse_content_return(tree.xpath('//span[@class="zm-profile-header-user-thanks"]/strong/text()'))
        self.user_info = self.parse_content_return(tree.xpath('//div[@class="bio dllipsis"]/text()'))
        self.user_introduction = self.parse_content_return(tree.xpath('//span[@class="info-wrap fold-wrap fold disable-fold"]/span[@class="fold-item"]/span/text()'))

        self.store_userdata_to_mongo()
        
        #用户关注的人的名单是JavaScript动态加载的，需要向‘https://www.zhihu.com/node/ProfileFolloweesListV2’（其Referer为当前用户的个人主页+/followees）
        #Form Data为：
        #method: next
        #params:{"offset": *, "order_by": "created", "hash_id": "字符串", "_xsrf":用户个人的xsrf值}
        #*：默认加载差值为20，即从0开始，20,40……，数据类型为int
        
        self.user_hashid = self.get_hashid(tree)
        self.user_following_list = []
        
        #多线程爬取单个用户关注的人
        page_list = [x for x in range(int(int(self.user_following_num)/20))]
        pool = Pool(os.cpu_count())
        result = pool.map_async(func=self.following_list_extend, iterable=page_list)
        pool.close()
        pool.join()

        return self.user_following_list
    
    #获取单页上关注的人列表
    def following_list_extend(self, pagenum):
        url_save = self.get_followees(pagenum*20)
        Lock().acquire()
        self.user_following_list.extend(url_save)
        time.sleep(1)
        print('Page %d is finished.' %(pagenum+1))
        Lock().release()

    #将信息存储在MongoDB上
    def store_userdata_to_mongo(self):
        new_profile = db.Zhihu_User_Profile(
            user_name = self.user_name,
            user_gender = self.user_gender,
            user_location = self.user_location,
            user_education_school = self.user_education_school,
            user_education_subject = self.user_education_subject,
            user_employment = self.user_employment,
            user_employment_extra = self.user_employment_extra,
            user_following_num = self.user_following_num,
            user_follower_num = self.user_follower_num,
            user_be_agreed_num = self.user_be_agreed_num,
            user_be_thanked_num = self.user_be_thanked_num,
            user_info = self.user_info,
            user_introduction = self.user_introduction,
        )
        new_profile.save()
        print('User %s, saved.' %self.user_name)
