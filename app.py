"""500_ticket_searcher"""
import random
import time
import csv
from py_topping.general_use import lazy_LINE
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import config


def ticket_searcher_of_500():
    """500_ticket_searcher"""

    # line api, keywords, group set up
    line = lazy_LINE(token=config.line_api)
    keywords_500 = ["五百", "伍佰", "伍百", "五佰", "chinablue",
                    "china blue", "Chinablue", "China Blue"]
    keywords_exclusion = ["求票"]
    keywords_scalper_ticket = ["代購"]

    groups_name = [
        ["演出票劵交流處", "https://www.facebook.com/groups/305645879554763"],
        ["演唱會門票買賣社區", "https://www.facebook.com/groups/hkticketconcert"],
        ["球賽票劵、演唱會票券、電影票、各式票 買賣社團", "https://www.facebook.com/groups/190369617822411"],
        ["台灣各大演唱會《售票、讓票、換票、周邊》交易交流社團",
            "https://www.facebook.com/groups/1512516018927091"],
        ["台灣 演唱會門票 販售 轉讓 求票", "https://www.facebook.com/groups/1384313241890049"],
        ["臺灣演唱會﹝讓票 / 換票 / 求票﹞專用社團", "https://www.facebook.com/groups/363530284163718"],
        ["演唱會原價讓票、換票、求票、售票", "https://www.facebook.com/groups/173192196733659"],
        ["演唱會門票轉讓平台", "https://www.facebook.com/groups/806336466161002"],
        ["演唱會 【讓票‧換票‧求票】 演唱會 門票 入場券",
            "https://www.facebook.com/groups/1614967552089919"],
        ["台灣熱門演唱會交流及轉讓社團", "https://www.facebook.com/groups/760953720661255"],
        ["【黃牛勿進】演唱會讓票換票求票", "https://www.facebook.com/groups/748278612014465"],
        ["票台灣演唱會各種求票讓票售票", "https://www.facebook.com/groups/630658917075030"]
    ]
    random.shuffle(groups_name)

    # open FB website and login

    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument('window-size=1920x1080')
    chrome = webdriver.Chrome("./chromedriver", chrome_options=options)
    chrome.get("https://www.facebook.com/")

    # login

    email = chrome.find_element(By.ID, "email")
    password = chrome.find_element(By.ID, "pass")
    email.send_keys(config.my_email)
    time.sleep(random.random()*2+1)
    password.send_keys(config.my_password)
    time.sleep(random.random()*2)
    password.submit()
    time.sleep(random.random()*2+3)

    # 進入group

    for group_number in enumerate(groups_name):

        print(f"Start getting posts from {group_number[1][0]}.")
        chrome.get(group_number[1][1])
        time.sleep(random.random()*2+3)

        # change filter to the lastest posts

        try:
            post_filter_most_relevant = chrome.find_element(
                By.XPATH, "//*[contains(text(), 'Most relevant')]")
            post_filter_most_relevant.click()
            time.sleep(random.random()*2+3)
            post_filter_new_post = chrome.find_element(
                By.XPATH, "//*[contains(text(), 'New posts')]")
            post_filter_new_post.click()

        except NoSuchElementException:
            post_filter_most_relevant = chrome.find_element(
                By.XPATH, "//*[contains(text(), 'Top listings')]")
            post_filter_most_relevant.click()
            time.sleep(random.random()*2+3)
            post_filter_new_post = chrome.find_element(
                By.XPATH, "//*[contains(text(), 'Nearby listings')]")
            post_filter_new_post.click()

        # 使用Python的迴圈，執行滾動捲軸3次

        for i in range(1, 4):
            chrome.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(random.random()*2+3)

        # create soup

        soup = BeautifulSoup(chrome.page_source, 'lxml')

        class_name_of_post = "m8h3af8h l7ghb35v kjdc1dyq kmwttqpk gh25dzvf n3t5jt4f"
        all_post_content = soup.find_all("div", {"class": class_name_of_post})

        # 呼叫shown content

        with open("./shown_content.csv", encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile)
            temp_list = list(reader)
            # flat the list
            shown_content_list = []
            shown_content_list = [
                item for sublist in temp_list for item in sublist]

        # 讀取post content, 判定是否提及500是否是舊文章

        for post_content in all_post_content:
            # 判定有沒有提及伍佰關鍵詞
            if any(word in str(post_content) for word in keywords_500):

                # 判定有沒有出現exclusion關鍵詞
                if any(word in str(post_content) for word in keywords_exclusion):
                    print("Mention 500 but not selling post")

                # 判定有沒有出現過在csv裡
                elif not post_content.getText() in shown_content_list:

                    # 判定是不是代購
                    scalper_ticket = ""
                    if any(word in str(post_content) for word in keywords_scalper_ticket):
                        scalper_ticket = "(代購)"

                    shown_content_list.append(post_content.getText())
                    message_to_line = f""" {scalper_ticket}
    New post from {group_number[1][0]}

    Content: {post_content.getText()}

    Link: {group_number[1][1]}"""
                    line.send(message_to_line)
                    print("Get new post: \n", post_content.getText())
                    print("Content stored and sent to line.")
                else:
                    print("Not new post")
            else:
                print("No mention of 500")
        print(f"{group_number[1][0]} is checked")

        # 資料寫回csv

        with open("./shown_content.csv", "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(shown_content_list)
        print("shown content was written back to csv")

    print("All groups are checked")
    print(shown_content_list)
    chrome.quit()


schedule.every(30).minutes.do(ticket_searcher_of_500)
ticket_searcher_of_500()

while 1:
    schedule.run_pending()
    time.sleep(1)
