import requests, re, time, os.path, http.cookiejar
from lxml import html
from PIL import Image


class Zhihu_Cookie(object):
    def __init__(self):
        self.headers = {}
        
        #为绕过知乎“倒立汉字验证码”以及其他Javascript加载，使用手机浏览器伪装请求
        self.headers['User-Agent'] = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit' \
                                     '/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
        self.headers['Host'] = 'www.zhihu.com'
        self.headers['Referer'] = 'https://www.zhihu.com'
        self.s = requests.session()
        self.s.cookies = http.cookiejar.LWPCookieJar(filename='cookies')

    #加载Cookie
    def session_mode(self):
        try:
            self.s.cookies.load(ignore_discard=True, ignore_expires=True)
        except:
            print('Cookie未能加载')

    #获取验证码
    def get_captcha(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = self.s.get(captcha_url, headers=self.headers)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()

        im = Image.open('captcha.jpg')
        im.show()
        im.close()

        captcha = input("please input the captcha\n> ")
        
        return captcha
    
    #通过查看用户个人信息来判断是否已经登录
    def isLogin(self):
        url = "https://www.zhihu.com/settings/profile"
        login_code = self.s.get(url, headers=self.headers, allow_redirects=False).status_code
        if login_code == 200:
            return True
        else:
            return False

    def login(self, account, password):
        
        #通过输入的用户名判断是否是手机号
        if re.match(r"^1\d{10}$", account):
            print("手机号登录 \n")
            post_url = 'https://www.zhihu.com/login/phone_num'
            postdata = {
                'password': password,
                'phone_num': account
            }
        else:
            if "@" in account:
                print("邮箱登录 \n")
            else:
                print("您的账号有误，请重新登录")
                account = input('请输入您的用户名\n> ')
                secret = input('请输入您的密码\n> ')
                self.login(account=account, password=password)
                return
            post_url = 'https://www.zhihu.com/login/email'
            postdata = {
                'password': password,
                'email': account
            }
        
        #不使用验证码登录
        headers = self.headers
        login_page = self.s.post(post_url, data=postdata, headers=headers)
        login_code = login_page.json()
        #不输入验证码登录失败，输入验证码
        if login_code['r'] == 1:
            postdata['captcha'] = self.get_captcha()
            login_page = self.s.post(post_url, data=postdata, headers=self.headers)
            login_code = login_page.json()
            print(login_code['msg'])
        #保存cookies,下次直接利用cookie登录
        self.s.cookies.save(ignore_discard=True, ignore_expires=True)
    
    #执行登录
    def login_execute(self):
        self.session_mode()
        if self.isLogin():
            print('您已经登录')
        else:
            account = input('请输入您的用户名\n> ')
            secret = input('请输入您的密码\n> ')
            self.login(account, secret)
