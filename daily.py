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
global First_Login_Time
global Second_Login_Time
global USER_NAME
global USER_PWD

def getImage(imgURL):    
    with open(imgURL, 'rb') as img:
            content = img.read()
            return content

def imgOcr(imagURL):
        img = getImage(imagURL)
        result = client.basicGeneral(img) #识别验证码
        for st in result['words_result']:
                try:
                        str = st['words']
                        num = int(str)
                except ValueError:
                        pass
                else:
                        return num
        return 0  #若图片中无数字,则返回数字0作为flag              

def login(user, pwd, dir):
        DiverUrl = dir + "\\driver\\chromedriver.exe"
        executable_path = {'executable_path':DiverUrl}
        if not os.path.exists(dir + "\\temp"):
                os.mkdir(dir + "\\temp")
        imagURL = dir + "\\temp\\ocr.jpg"
        loginFlag = True
        dailyFlag = True
        browser = Browser("chrome", **executable_path)
        while(loginFlag or dailyFlag): #循环直到打卡成功
                try:
                        alert = browser.get_alert() #如果有代理登陆提示,则点击取消
                except Exception:
                        pass
                else:
                        alert.dismiss()                             
                try:
                        if loginFlag: #将登陆与打卡动作分离,便于判断
                                browser.visit("http://kq.neusoft.com")
                                input = browser.find_by_tag("input")
                                input[4].fill(user)
                                input[5].fill(pwd)
                                screenshot_path = browser.find_by_id("tbLogonPanel").screenshot(imagURL, full=True) #因单独截取验证码图片会出现偏离而无法识别,故而截取整个Form,再对识别结果进行处理,最终返回一个截图的路径
                                ocrResult = imgOcr(screenshot_path)
                                os.remove(screenshot_path) #删除验证码截图
                                if ocrResult is 0: #避免识别错误导致页面刷新从而出现bug
                                        logOut("图片路径:" + screenshot_path + ",识别失败")
                                        continue
                                print(time.strftime("%D %H:%M:%S", time.localtime()), "识别验证码为:", ocrResult)
                                input[6].fill(ocrResult) #填入验证码识别结果
                                browser.find_by_id("loginButton").click() #点击登陆按钮
                                if browser.is_text_present('打卡'):
                                        loginFlag = False
                                        logOut("登陆成功")
                        if dailyFlag:
                                timeNow = time.strftime("%H:%M", time.localtime())
                                browser.find_by_text("打卡").first.click()#直接执行js语句
                                if browser.find_by_tag("tr").last.find_by_tag("td").last.text[0:5] == timeNow:
                                        dailyFlag = False
                                        logOut("打卡成功")
                except Exception as identify:
                        logOut("打卡失败:" + str(identify)) #直接进入下一循环 
        browser.quit()                    

def init_time(): #初始化打卡时间
        global First_Login_Time
        global Second_Login_Time
        First_Login_Time = "08:" + str(randint(0, 39) + 20)
        logOut("First_Login_Time:" + First_Login_Time)
        Second_Login_Time = "18:" + str(randint(0, 49) + 10)
        logOut("Second_Login_Time:" + Second_Login_Time)

def logOut(content): #日志处理方法
        content = time.strftime("%D %H:%M:%S ", time.localtime()) + content #记录当前时间
        print(content) #命令行中输出日志
        with open("D:\\daily\\log.txt", "a+") as log:
                log.write(content) #向log文件写入日志

def init_config(DIR_NAME): #初始化配置方法
        global USER_NAME  #采用全局变量方法
        global USER_PWD
        DiverUrl = DIR_NAME + "\\driver"
        if not os.path.exists(DIR_NAME):
                os.mkdir(DIR_NAME)
        if not os.path.exists(DiverUrl):
                os.mkdir(DiverUrl) #初始化driver路径
        while os.path.exists(DiverUrl+"\\chromedriver.exe") == False: #确认driver文件就位
                input("请确认已将chromedriver文件放置于:" + DiverUrl + "\\路径下? (y/n) ")
        try:
                config = open(DIR_NAME+"\\config.txt") #读取配置文件
        except FileNotFoundError: #异常处理(即首次运行时新建配置文件)
                config = open(DIR_NAME+"\\config.txt", "w")
                USER_NAME = input("please input your user_name:")
                config.write(USER_NAME + "\n")
                USER_PWD = input("please input your password:")
                config.write(USER_PWD)
                config.close                  
        else:
                configs = config.readlines()
                USER_NAME = configs[0].rstrip() #注意消去每一行末尾的空格
                USER_PWD = configs[1].rstrip()
                config.close

while True:
        # 判断条件
        timeNow = time.strftime("%H:%M", time.localtime())
        weekDay = time.strftime("%w", time.localtime())
        if(First_Login):
                logOut("------ Begin init config ------")
                # 首次登陆从配置文件中读取用户名及密码
                DIR_NAME = "D:\\daily" #默认路径
                init_config(DIR_NAME)  #初始化个人配置                                         
                init_time()                     
                First_Login = False
                login(USER_NAME,USER_PWD,DIR_NAME) #根据全局配置进行打卡
        if(time.strftime("%H:%M", time.localtime()) == "00:00"): 
                init_time()
        if((timeNow == First_Login_Time or timeNow == Second_Login_Time)and not(weekDay == "0" or weekDay == "6")): #1.越过周六与周日;2.时钟与分钟一致时启动打卡
                login(USER_NAME,USER_PWD,DIR_NAME) #根据全局配置进行打卡
        time.sleep(60) #延时60秒