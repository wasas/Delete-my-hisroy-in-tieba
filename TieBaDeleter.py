# -*- coding: utf-8 -*-

import re
import time
import urllib.request

from selenium import common, webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def login(username, password):
    print("Spider started")
    urlusername = urllib.request.quote(username)
    driver.get("http://tieba.baidu.com/home/main?un=" + urlusername + "&fr=home")
    driver.find_element_by_class_name("u_login").click()
    time.sleep(2)

    pageSouce = driver.page_source
    elementidPrefix = re.findall(r"(TANGRAM__PSP_[0-9]{1,})__footerULoginBtn", pageSouce)[0]

    driver.find_element_by_id(elementidPrefix + "__footerULoginBtn").click()
    driver.find_element_by_id(elementidPrefix + "__userName").send_keys(username)
    driver.find_element_by_id(elementidPrefix + "__password").send_keys(password)
    driver.find_element_by_id(elementidPrefix + "__submit").click()
    time.sleep(3)


def my_tie_collector():
    driver.get("http://tieba.baidu.com/i/i/my_tie")
    listOfLinks = list()
    listOfElements = driver.find_elements_by_class_name("thread_title")
    for i in range(0, len(listOfElements)):
        listOfLinks.append(listOfElements[i].get_attribute("href"))

    driver.get("http://tieba.baidu.com/i/i/my_tie?&pn=2")  #每天限制30贴，所以最多前两页就足够了
    listOfElements = driver.find_elements_by_class_name("thread_title")
    for i in range(0, len(listOfElements)):
        listOfLinks.append(listOfElements[i].get_attribute("href"))

    print("Links of Tie Collected")
    return listOfLinks


def my_reply_collector():
    driver.get("http://tieba.baidu.com/i/i/my_reply")
    listOfLinks = list()
    listOfElements = driver.find_elements_by_class_name("for_reply_context")
    for i in range(0, len(listOfElements)):
        listOfLinks.append(listOfElements[i].get_attribute("href"))

    driver.get("http://tieba.baidu.com/i/i/my_reply?pn=2")  #同上
    listOfElements = driver.find_elements_by_class_name("for_reply_context")
    for i in range(0, len(listOfElements)):
        listOfLinks.append(listOfElements[i].get_attribute("href"))

    print("Links of Reply Collected")
    return listOfLinks


def deleter_tie(listOfLinks, username):  #增加对楼中楼的删除功能
    print("Now Deleting")
    for i in range(0, len(listOfLinks)):
        try:
            driver.get(listOfLinks[i])
            time.sleep(1)
            element = driver.find_element_by_class_name("p_post_del_my")
            driver.execute_script("arguments[0].scrollIntoView(false);", element)
            element.click()
            time.sleep(0.3)
            driver.find_element_by_class_name("dialogJanswers").find_element_by_tag_name("input").click()
            print("Deleted")
            continue
        except common.exceptions.NoSuchElementException:
            print("Fail to find element, try next way")

        try:
            maincontent = driver.find_element_by_class_name("p_postlist")
            elements = maincontent.find_elements_by_link_text(username)
            for element in elements:
                ActionChains(driver).move_to_element(element).perform()
                try:
                    driver.find_element_by_link_text("删除").click()
                    break
                except common.exceptions.NoSuchElementException:
                    print("Fail to find element, try next herf")  #有可能别人@你导致选错元素，所以对每个超链接遍历一遍直到找到有删除按钮的
            time.sleep(0.3)
            driver.find_element_by_class_name("dialogJanswers").find_element_by_tag_name("input").click()
            print("Deleted")
        except common.exceptions.NoSuchElementException:
            print("Fail to find element, maybe your are in anonymous")


def deleter_follows():
    while True:
        driver.get("http://tieba.baidu.com/i/i/concern")
        try:
            driver.find_element_by_class_name("btn_unfollow").click()
            driver.find_element_by_class_name("dialogJbtn").click()
            time.sleep(0.5)
        except common.exceptions.NoSuchElementException:
            print("Follows has been all deleted")
            break


def deleter_fans():
    while True:
        driver.get("http://tieba.baidu.com/i/i/fans")
        try:
            element = driver.find_element_by_class_name("name")
            ActionChains(driver).move_to_element(element).perform()  #移动到名字否则取消关注不会出现
            driver.find_element_by_id("add_blacklist_btn").click()
            driver.find_element_by_class_name("dialogJbtn").click()
            time.sleep(0.5)
        except common.exceptions.NoSuchElementException:
            print("Fans has been all deleted")
            break


def deleter_BaIFollow():  #使用此功能需打开图片显示
    driver.get("http://tieba.baidu.com/i/i/forum")
    driver.find_element_by_class_name("pm_i_know").click()
    while True:
        try:
            driver.find_element_by_class_name("pt").click()
            driver.find_element_by_class_name("dialogJbtn").click()
            time.sleep(0.5)
        except common.exceptions.NoSuchElementException:
            print("BaIFollows has been all deleted")
            break


def Start_with_Chrome_without_images():
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def Start_with_Chrome():
    driver = webdriver.Chrome()
    return driver

#driver = Start_with_Chrome_without_images()  #不加载图片可以提高速度但是无法删除关注的贴吧
driver = Start_with_Chrome()
login("Here is your username", "Here is your password")
deleter_tie(my_tie_collector(), "Here is your username")
deleter_fans()
deleter_follows()
deleter_BaIFollow()
print("All done")
