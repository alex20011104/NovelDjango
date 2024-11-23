import requests
from bs4 import BeautifulSoup
import pymysql

class novel():
    con = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        db="novel",
        charset="utf8mb4"
    )
    # 创建游标对象
    mycursor = con.cursor()

    def __init__(self):
        self.url = "https://top.baidu.com/board?tab=novel"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    def send_request(self, url):
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp

    def parse_html(self, resp):
        lst = []
        html = resp.text
        soup = BeautifulSoup(html,"html.parser")
        div = soup.findAll("div",class_="content_1YWBm")
        for item in div:
            novel_name = item.find("div",class_="c-single-text-ellipsis").text
            sub_item_list = item.findAll("div", class_="intro_1l0wp")
            author = sub_item_list[0].text
            category = sub_item_list[1].text
            description = item.find("div",class_="c-single-text-ellipsis desc_3CTjT").text
            description = description.replace("查看更多> ", "")
            # print(novel_name,author,category,description)
            lst.append((novel_name,author,description,category))
        self.save(lst)

    def save(self, lst):
        # print(self.con)
        sql='INSERT INTO novel (novel_title, author, description, category) VALUES (%s, %s, %s, %s);'
        self.mycursor.executemany(sql,lst)
        self.con.commit()
        print(self.mycursor.rowcount,"插入完毕")

    def start(self):
        # for i in range(1,2):
        #     full_url=self.url.format(i)
        url = self.url
        resp = self.send_request(url)
        # print(resp.text)
        self.parse_html(resp)



if __name__ == '__main__':
    novel = novel()
    novel.start()
