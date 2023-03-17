from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import asyncio


def open_url(username, password):
    options = webdriver.ChromeOptions()
    # prefs = {"profile.managed_default_content_settings.images": 2}  # 设置无图模式
    # options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(10)
    url = "https://webvpn.chzu.edu.cn/https/webvpn6d79302e63687a752e6564752e636e/link?id=aa13361944680028&url=https%3A%2F%2Fyq.weishao.com.cn%2Fcheck%2Fquestionnaire "
    try:
        browser.get(url)
        print("starting...")
    except TimeoutException:
        print('Time Out')
    try:
        iframe = browser.find_element(By.TAG_NAME, 'iframe')
        browser.switch_to.frame(iframe)
        select = Select(browser.find_element(By.ID, 'schoolcode'))
        select.select_by_value(value='chzu')
        time.sleep(0.2)
        browser.find_element(By.ID, 'username').send_keys(username)
        time.sleep(0.2)
        browser.find_element(By.ID, 'password').send_keys(password)
        time.sleep(0.2)
        browser.find_element(By.ID, 'btnpc').click()
        time.sleep(0.2)
        try:
            browser.find_element(By.CLASS_NAME, "statusCode")
            print("*" * 47)
            print(f"{username}----账号或密码错误！也或许服务器错误！")
            print("*" * 47)
        except:
            try:
                browser.find_element(By.CLASS_NAME, 'p1').click()
                try:
                    browser.find_element(By.CLASS_NAME, "public_modal_tax")
                    print("!" * 47)
                    print(f"{username}----今天已经完成打卡！！请不要重复打开此页面！！")
                    print("!" * 47)
                except:
                    time.sleep(0.2)
                    browser.find_elements(By.CLASS_NAME, 'am-modal-button')[1].click()
                    time.sleep(0.2)
                    button = browser.find_elements(By.CLASS_NAME, 'btn_xs')[1]
                    ActionChains(browser).move_to_element(button).click(button).perform()
                    print("+" * 47)
                    print(f"{username}----完成打卡")
                    print("+" * 47)
            except NoSuchElementException:
                print('Hello! No Element')
            except IndexError:
                print('Hello! No View')
            except WebDriverException:
                print("Hello! Abnormal Condition")
    finally:

        time.sleep(2)
        browser.close()


def main():
    dict_user = {

    }
    # 让用户每次输入学号和密码(繁琐)
    # polling_active = True
    # while polling_active:
    #     print("添加打卡人员")
    #     username = input("username: ")
    #     password = input("password: ")
    #     dict_user.update({username: password})
    #     repeat = input("是否继续输入:(yes/no)")
    #     if repeat == "no":
    #         polling_active = False
    for key, value in dict_user.items():
        open_url(key, value)
        print('ending...')


if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2-t1)
