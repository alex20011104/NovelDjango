import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime


class novel():
    con = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        db="novels",
        charset="utf8"
    )
    # 创建游标对象
    mycursor = con.cursor()

    def __init__(self):
        self.url = "https://www.qidian.com/rank/hotsales/"
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
        li = soup.findAll("li",attrs={'data-rid': True})
        for item in li:
            #小说网址
            url = item.find("a", attrs={'data-eid': 'qd_C39'})
            novellist = "https:" + url["href"] + "#Catalog"

            # 图片网址
            imgbox = item.find("div",class_='book-img-box')
            img = imgbox.find('img')
            url = 'https:' + img['src']

            #小说名称
            name = item.find("h2").text

            #详情
            p = item.find("p",class_='author')
            author = p.find("a",class_='name').text
            category = p.find("a",attrs={'data-eid': 'qd_C42'}).text
            state = p.find("span").text
            description = item.find("p",class_='intro').text

            current_time = datetime.now().replace(microsecond=0)  # 获取当前时间
            pa_state_default = 0
            print(url, name, author, category, state, description, novellist, current_time)
            lst.append((url, name, author, category, state, description, novellist, current_time, pa_state_default))
        self.save(lst)

    def save(self, lst):
        # print(self.con)

        sql='INSERT INTO novel (cover, novel_title, author, category, state, description, novellist, pa_time, pa_state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'
        self.mycursor.executemany(sql,lst)
        self.con.commit()
        print(self.mycursor.rowcount,"插入完毕")

    def start(self):
        # for i in range(1,2):
        #     full_url=self.url.format(i)
        page_count = 5  # 设置要爬取的总页数
        for i in range(1, page_count + 1):
            if i == 1:
                url = self.url
            else:
                url = f"{self.url}/page{i}"
            resp = self.send_request(url)
            self.parse_html(resp)



if __name__ == '__main__':
    novel = novel()
    novel.start()
