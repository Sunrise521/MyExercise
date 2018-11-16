from splinter import Browser
from random import randint
import time
import os
from aip import AipOcr
"""配置APPID"""
APP_ID = "10737691"
API_KEY = "Td4SduTbOaEu0WSUUPo5KxEx"
SECRET_KEY = "roP2CCVBQQALmy66buvR9wS6vNQKQ1DA"
proxies = {"http" : "http://def:qwertgfdsa@10.1.24.38:3333", "https" : "https://def:qwertgfdsa@10.1.24.38:3333"}
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
client.setProxies(proxies)  #设置http代理 
First_Login = True
Second_Login = False
global First_Login_Time
First_Login_Time = "08:45"
global Second_Login_Time
Second_Login_Time = "18:15"
global USER_NAME
# USER_NAME = ""
global USER_PWD
# USER_PWD = ""

def getImage(imgURL):    
    with open(imgURL, 'rb') as img:
            content = img.read()
            return content

def imgOcr(imagURL):
        # imagURL = "D:\\Alan\\Pictures\\背景.jpg"
        img = getImage(imagURL)
        result = client.basicGeneral(img)
        for st in result['words_result']:
                try:
                        str = st['words']
                        num = int(str)
                except ValueError:
                        pass
                else:
                        return num                

def login(user, pwd, dir):
        DiverUrl = dir + "\\driver\\firefoxdriver.exe"
        executable_path = {'executable_path':DiverUrl}     
        try:
                browser = Browser("firefox", **executable_path)
                browser.visit("http://kq.neusoft.com")
                # input = browser.find_by_tag("input")
                browser.find_by_tag("input")[4].fill(user)
                browser.find_by_tag("input")[5].fill(pwd)
                if not os.path.exists(dir + "\\temp"):
                        os.mkdir(dir + "\\temp")
                imagURL = dir + "\\temp\\ocr.jpg"
                screenshot_path = browser.find_by_id("tbLogonPanel").screenshot(imagURL, full=True)
                ocrResult = imgOcr(screenshot_path)
                browser.find_by_tag("input")[6].fill(ocrResult)
                browser.find_by_id("loginButton").click()
                time.sleep(3)
                # a = browser.find_by_tag("a")
                browser.execute_script('$(".mr36")[0].click()')
                time.sleep(1)
                browser.quit()
        except Exception as identify:
                logOut(str(identify))
                print(time.strftime("%H:%M:%S", time.localtime()), "打卡失败")
        else:
                print(time.strftime("%H:%M:%S", time.localtime()), "打卡成功")        

def init_time():
        global First_Login_Time
        global Second_Login_Time
        First_Login_Time = "08:" + str(randint(0, 30) + 29)
        print("First_Login_Time:",First_Login_Time)
        Second_Login_Time = "18:" + str(randint(0, 30) + 10)
        print("Second_Login_Time", Second_Login_Time)

def logOut(content):
        with open("D:\\daily\\log.txt", "a") as log:
                log.write(time.strftime("%H:%M:%S", time.localtime()) + ": " + content + "\n")

def init_config(DIR_NAME):
        global USER_NAME
        global USER_PWD
        DiverUrl = DIR_NAME + "\\driver"
        if not os.path.exists(DIR_NAME):
                        os.mkdir(DIR_NAME)
                        if not os.path.exists(DiverUrl):
                                os.mkdir(DiverUrl)
                                print("请将firefoxdriver文件放置于:" + DiverUrl + "路径下")
        with open(DIR_NAME + "\\log.txt","w") as log:
                        log.write("----begin init config----\n")
        try:
                config = open(DIR_NAME+"\\config.txt")
        except FileNotFoundError:
                config = open(DIR_NAME+"\\config.txt", "w")
                USER_NAME = input("please input your user_name:")
                config.write(USER_NAME + "\n")
                USER_PWD = input("please input your password:")
                config.write(USER_PWD)
                config.close                  
        else:
                configs = config.readlines()
                USER_NAME = configs[0].rstrip()
                USER_PWD = configs[1].rstrip()
                config.close
        logOut("Let's Begin!")

while True:
        # 判断条件
        timeNow = time.strftime("%H:%M", time.localtime())
        weekDay = time.strftime("%w", time.localtime())
        if(First_Login):
                # 首次登陆从配置文件中读取用户名及密码
                DIR_NAME = "D:\\daily"
                init_config(DIR_NAME)                                           
                init_time()                     
                First_Login = False
                login(USER_NAME,USER_PWD,DIR_NAME)
        if(time.strftime("%H:%M", time.localtime()) == "00:00"):
                init_time()
        if(timeNow == First_Login_Time or timeNow == Second_Login_Time and not(weekDay == "5" or weekDay == "6")):
        # if(True):
                login(USER_NAME,USER_PWD,DIR_NAME)
        time.sleep(60)