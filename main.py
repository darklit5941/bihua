import os, time
import urllib.request
from urllib.parse import urlparse
from urllib.parse import parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://bihua.topschool.tw/Activity/Class-Albums")

UserName= ('bihuap010')
UserPass= ('82168216')

el = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "account"))
el.send_keys(UserName)
el = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "password"))
el.send_keys(UserPass)
el.send_keys(Keys.ENTER)

time.sleep(3)
driver.get("https://bihua.topschool.tw/Activity/Class-Albums?PageIndex=1")
time.sleep(1)

# 抓所有相簿
elems = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CLASS_NAME, "albumbgphoto"))
items = []
for elem in elems:
    albumId = parse_qs(urlparse(elem.get_attribute('href')).query)['albumId'][0]
    link = "https://bihua.topschool.tw/Activity/Class-Album-Detail?albumId={}&pageIndex=1".format(albumId)
    div = elem.find_element(By.XPATH, "./../../div[contains(@class, 'info')]/div")
    items.append({
        'link': link,
        'name': div.text
    })

for item in items:
    # 抓所有照片
    dirName = item['name']
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    folderPath = os.path.join(os.getcwd(), dirName)
    print(folderPath)
    driver.get(item['link'])

    while True:
        #抓取這頁照片
        elems = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CLASS_NAME, "photo-gallery"))
        links = [elem.get_attribute('href') for elem in elems]
        for link in links:
            fileName = urlparse(link).path
            urllib.request.urlretrieve(link, folderPath + fileName)
        #換頁再抓
        try:
            next = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH, "//ul[contains(@class, 'pagination')]/li[contains(@class, 'active')]/following-sibling::li[1]/a"))
        except TimeoutException as exception:
            print('這個相簿只有一頁')   
            break
        if None != next.get_attribute('href'):
            print('還有下一頁' + next.get_attribute('href'))
            next.click()
        else:
            print('這個相簿沒了')
            break


time.sleep(3)