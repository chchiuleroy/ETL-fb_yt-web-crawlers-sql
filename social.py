# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 10:20:15 2020

@author: user
"""

from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine, MetaData, Table
from selenium import webdriver
from retrying import retry
import pandas as pd, time

@retry(stop_max_attempt_number = 100)
def url_get():
    tunnel = SSHTunnelForwarder(('event.ai.hinet.net', 22), ssh_password = '9m0z58aFuF50F97ZHri', ssh_username = 'root', remote_bind_address = ('127.0.0.1', 3306)) 
    tunnel.start()
    user = 'root'; password = 'WuT1nh2do3emr45pm6@saonn'; port = tunnel.local_bind_port; host = '127.0.0.1'; db = 'ibaby'
    engine = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + ':' + str(port) + '/' + db)
    time.sleep(1)
    metadata = MetaData(engine)
    time.sleep(1)
    user_table = Table('poster_info', metadata, autoload = True)
    time.sleep(1)
    conn = engine.connect()
    rs = conn.execute('SELECT * FROM poster_info')
    row = [j for j in rs]
    need = pd.DataFrame(row)
    # need.columns
    url = need.iloc[:, 5]
    return url, need, conn, user_table

url, need, conn, user_table = url_get()

fb = url.str.find('www.facebook.com')
yt = url.str.find('www.youtube.com')

temp = url[yt>-1]
account = temp.str.split('/').str[4]
url[yt>-1] = ['https://www.youtube.com/watch?v=' + account.iloc[i] + '&feature=emb_title' for i in range(len(temp))]

s1 = 'CHBHLCBGEGBHEGHDFDEDMDFECHAHLGBGAGHHIGEGLGBHNGKGIGFHGHKGLGLCGGKGIG'
s2 = 'IEEGHHGGNGHDFDHDFDEC'

def decrypt(key, s): 
    code = 'gbk'
    c = bytearray(str(s).encode(code)) 
    n = len(c)
    if n % 2 != 0 : 
        return "" 
    n = n // 2 
    b = bytearray(n) 
    j = 0 
    for i in range(0, n): 
        c1 = c[j] 
        c2 = c[j+1] 
        j = j+2 
        c1 = c1 - 65 
        c2 = c2 - 65 
        b2 = c2*16 + c1 
        b1 = b2^ key 
        b[i]= b1 
    try: 
        return b.decode(code) 
    except: 
        return 'failed' 

def get_fb_like(url):
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument('--disable-popup-blocking')
    options.add_argument('disable-infobars') 
    # options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    # options.add_argument('--headless') #無頭模式
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')
    
    # browser = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options = options)
    browser = webdriver.Chrome(chrome_options = options)
    browser.set_window_size(1920, 800)
    browser.get('http://www.facebook.com')
    time.sleep(2)
    browser.find_element_by_id('email').send_keys(decrypt(5, s1)) 
    browser.find_element_by_id('pass').send_keys(decrypt(5, s2))
    browser.find_element_by_id('u_0_b').click()
    time.sleep(3)
    def get_likes(url):
        browser.get(url)
        time.sleep(2)
        num = browser.find_elements_by_class_name('pcp91wgn')
        time.sleep(2)
        a = []
        for j in range(len(num)):
            try:
                a.append(int(num[j].text))
            except:
                a.append('')
        return list(set(a))[-1]
    num = [get_likes(url.iloc[i]) for i in range(len(url))]        
    browser.close()
    return num

def get_yt_like(html):
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument('--disable-popup-blocking')
    options.add_argument('disable-infobars') 
    
    browser = webdriver.Chrome(options = options)
    # browser.implicitly_wait(30) 
    browser.set_window_size(1920, 800)
    def get_like(html):
        try:
            browser.get(html)
            time.sleep(2)
            x_path = "//div[@id='menu-container']/div/ytd-menu-renderer/div/ytd-toggle-button-renderer[1]/a/yt-formatted-string"
            nice_count = browser.find_element_by_xpath(x_path).text
        except:
            nice_count = ''
        return nice_count
    num = [get_like(html.iloc[i]) for i in range(len(html))]
    browser.close()
    return num

fb_likes = get_fb_like(url[fb>-1])
yt_likes = get_yt_like(url[yt>-1])

likes = pd.Series(['']*len(url))
likes[fb>-1] = fb_likes
likes[yt>-1] = yt_likes
# url[likes==''].tolist()
likes[15] = 94
likes[16] = 0
likes[17] = 112
likes[18] = 0
likes[23] = 0
likes[38] = 2
# likes[21] = 0
f = likes.astype(int).tolist()
print(f)
uid = need.iloc[:, 0].tolist()
for j in range(len(f)):
    user_table.update().where(user_table.c.uid == uid[j]).values({'likes_count': f[j]}).execute()
del j
# user_table.delete().where(user_table.c.likes_count == 3).execute()
conn.close()
