from mi.spiders.hiaas_common import *
from time import sleep

class NaverLogin(Login):

    LoginUrl = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'
    ID = 'swpark_hiaas'
    PW = 'hiaas12!@'
    IDElement = '//*[@id="id"]'
    PWElement = '//*[@id="pw"]'
    LoginBtnElement = '//*[@id="log.login"]'

    # def __init__(self, page):
    #     self.page = page
    #     page.goto(self.LoginUrl)
    
    def setup(self, page):
        print('접속')
        self.page = page
        page.goto(self.LoginUrl)
        sleep(2.0)
        # page.screenshot(path='login.png', full_page=True)
        # self.page.locator('//*[@id="gateway"]/div/div[2]/div/ul/li[1]/a').click()
        # sleep(2.0)
        page.screenshot(path='naverLoginPage.png', full_page=True)        
        # page.goto(self.url)
        print('접속 ok')

    def InputID(self):
        self.page.locator(self.IDElement).fill(self.ID)

    def InputPasswd(self):
        self.page.locator(self.PWElement).fill(self.PW)

    def ClickLogInBtn(self):
        self.page.locator(self.LoginBtnElement).click()