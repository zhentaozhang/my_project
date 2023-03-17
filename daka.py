import time
from multiprocessing import Pool

from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def open_url(username, password):
    options = webdriver.ChromeOptions()
    # prefs = {"profile.managed_default_content_settings.images": 2}  # 设置无图模式
    # options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument('--headless')  # 设置无头模式
    s = Service(executable_path=r"D:\日常软件\pycharm\pythonProject\venv\Scripts\chromedriver.exe")
    browser = webdriver.Chrome(service=s, options=options)
    browser.implicitly_wait(10)
    url = "https://webvpn.chzu.edu.cn/https/webvpn6d79302e63687a752e6564752e636e/link?id=aa13361944680028&url=https%3A%2F%2Fyq.weishao.com.cn%2Fcheck%2Fquestionnaire"
    browser.get(url)
    print("starting...")
    try:
        iframe = browser.find_element(By.TAG_NAME, 'iframe')  # 获取Url的子页面
        browser.switch_to.frame(iframe)
        select = Select(browser.find_element(By.ID, "schoolcode"))
        select.select_by_value(value='chzu')
        time.sleep(0.5)
        browser.find_element(By.ID, 'username').send_keys(username)
        time.sleep(0.5)
        browser.find_element(By.ID, 'password').send_keys(password)
        time.sleep(0.5)
        browser.find_element(By.ID, 'btnpc').click()  # 点击登录按钮
        time.sleep(0.5)
        click_html = browser.page_source  # 获取点击按钮后跳转页面的HTML
        doc = pq(click_html)
        if doc('.statusCode').text() == "状态码：500":
            # 如果登陆失败，页面显示状态码：500
            # 通过获取HTML页面内容获取元素比使用.find_element性能更高
            print("*" * 47)
            print(f"{username}----账号或密码错误！也或许服务器错误！")
            print("*" * 47)
        else:
            browser.find_element(By.CLASS_NAME, 'p1').click()
            # 正常登录
            time.sleep(0.5)
            doc_1 = pq(browser.page_source)
            # 与上行代码类似
            if doc_1('.public_modal_tax').text() == "您在周期内已填写过此问卷, 1天后可再次填写，请前往\"我的-我填写的\"页面查看详情":
                # 如果今天已经完成打卡
                print("!" * 47)
                print(f"{username}----今天已经完成打卡！！请不要重复打开此页面！！")
                print("!" * 47)
            else:
                try:
                    browser.find_elements(By.CLASS_NAME, 'am-modal-button')[1].click()
                    # 正常情况，点击元素进行打卡
                    time.sleep(0.2)
                    button = browser.find_elements(By.CLASS_NAME, 'btn_xs')[1]
                    ActionChains(browser).move_to_element(button).click(button).perform()
                    print("+" * 47)
                    print(f"{username}----完成打卡")
                    print("+" * 47)
                except NoSuchElementException:
                    print('Hello! No Element')
                # except IndexError:
                #     print('Hello! IndexError')
                # except WebDriverException:
                #     print("Hello! WebDriverException")
    except TimeoutException:
        print('Time Out')
    finally:
        time.sleep(2)
        browser.close()


if __name__ == '__main__':
    dict_user = {
     
    }
    pool = Pool()
    t1 = time.time()
    item = [i for i in dict_user.items()]
    pool.starmap(open_url, item)
    t2 = time.time()
    print(t2 - t1)
