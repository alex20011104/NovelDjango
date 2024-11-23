# from django.contrib import admin
#
# # Register your models here.
# from .models import User, novel
#
# admin.site.register(User)
# admin.site.register(novel)
from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html
from datetime import datetime
from api.models import User, novel, Score, Comment, Chapter, Category, History, Cover, Mail

import requests
from bs4 import BeautifulSoup
import pymysql
import pickle


class NovelSpider():
    con = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        db="novels",
        charset="utf8mb4"
    )
    # 创建游标对象
    mycursor = con.cursor()

    def __init__(self, novel_id, url):
        self.novel_id = novel_id
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            # 'User-Agent':'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57'
        }


    def send_request(self, url):
        resp = requests.get(url, headers=self.headers)
        print(url)
        if resp.status_code == 200:
            return resp

    def parse_html(self, resp):
        lst = []
        chapter = []
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        h2 = soup.findAll("h2", class_="book_name")
        for item in h2:
            link = item.find("a")
            url = link["href"]
            title = link.text
            lst.append((url, title))
        count = 0  # 添加计数器
        for link, title in lst:
            if count >= 5:  # 如果已经爬取了30章，就退出循环
                break
            link ='https:' +link
            print(title)
            max_retry = 3  # 重试次数
            for i in range(max_retry):
                response = requests.get(link, headers=self.headers)
                content = response.text
                soup = BeautifulSoup(content, "html.parser")

                div = soup.find("main", class_="content mt-1.5em text-s-gray-900 leading-[1.8] relative z-0 r-font-black")

                if div is not None:
                    break  # 如果获取到内容，就退出循环
            if div is None:  # 如果尝试max_retry次后仍然没有获取到内容，就打印错误信息并跳过这一章
                div = '此章节被爬取失败'
                count += 1
                continue

            chapter.append((self.novel_id, title, div.text.replace("\u3000", " ")))
            count += 1  # 在成功爬取一章之后，计数器加1
            print(count)
        # print(chapter)
        with open('chapterWX.pkl', 'wb') as f:
            pickle.dump(chapter, f)
        self.save(chapter)

    def save(self, chapter):
        # print(self.con)
        sql='INSERT INTO chapter (novel_id, chapter_title, content) VALUES (%s, %s, %s);'
        self.mycursor.executemany(sql,chapter)
        self.con.commit()
        print(self.mycursor.rowcount,"插入完毕")



    def load_and_save_chapter_data(self):
        with open('chapterWX.pkl', 'rb') as f:
            chapter_data = pickle.load(f)
        self.save(chapter_data)

    def start(self):
        # for i in range(1,2):
        #     full_url=self.url.format(i)
        print('开始爬取')
        url = self.url
        resp = self.send_request(url)
        # print(resp.text)
        self.parse_html(resp)

# if __name__ == '__main__':
#     novel = novel()
#     novel.load_and_save_chapter_data()

if __name__ == '__main__':
    novel = novel()
    novel.start()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'password', 'gender', 'age')
    list_per_page = 15
    ordering = ('user_id',)
    list_display_links = ('user_id', 'username')
    search_fields = ('username', 'user_id')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(novel)
class NovelAdmin(admin.ModelAdmin):

    list_display = ('novel_id', 'cover_image', 'novel_title', 'author', 'short_description', 'category', 'state', 'pa_time', 'pa_state')
    list_per_page = 15
    ordering = ('novel_id',)
    list_display_links = ('novel_id', 'novel_title')
    search_fields = ('novel_title', 'author')
    # exclude = ('pa_time', 'pa_state')  # 在编辑表单中排除这两个字段
    # 增加自定义按钮
    actions = ['pychapter']

    # 定义 pa_time 和 pa_state 字段的属性
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'pa_time':
            db_field.null = True
            db_field.blank = True
        if db_field.name == 'pa_state':
            db_field.blank = True
        return super().formfield_for_dbfield(db_field, **kwargs)

    def pychapter(self, request, queryset):
        for novel in queryset:
            novel_spider = NovelSpider(novel.novel_id, novel.novellist)
            novel_spider.start()
            novel.pa_state = 1  # 更新爬虫状态
            novel.pa_time = datetime.now().replace(microsecond=0)  # 插入爬虫时间
            novel.save()
        self.message_user(request, '爬虫程序完成', level=messages.SUCCESS)  # 显示提示信息
        print(novel.novel_title,'插入完成')

    # 显示的文本，与django admin一致
    pychapter.short_description = '章节导入'
    # icon，参考element-ui icon与https://fontawesome.com
    pychapter.icon = 'fas fa-audio-description'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    pychapter.type = 'success'

    # 给按钮追加自定义的颜色
    pychapter.style = 'color:black;'



    def cover_image(self, obj):
        return format_html('<img src="{}" width="50" height="70" />', obj.cover)
    cover_image.short_description = u'封面'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def short_description(self, obj):
        return obj.description[:30] + '...' if len(obj.description) > 30 else obj.description

    short_description.short_description = '简介'

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'novel_title',  'favorite', 'score')
    list_per_page = 15
    ordering = ('novel',)
    list_display_links = ('user_name', 'novel_title')
    search_fields = ('user__username', 'novel__novel_title')

    def user_name(self, obj):
        return obj.user.username

    user_name.short_description = '用户名'  # 设置列的标题

    def novel_title(self, obj):
        return obj.novel.novel_title

    novel_title.short_description = '小说名'  # 设置列的标题

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'comment_content', 'created_time', 'user_name', 'novel_title')
    readonly_fields = ('user_name', 'novel_title')  # 设置为只读
    exclude = ('user', 'novel')  # 在编辑表单中排除这两个字段
    list_per_page = 15
    ordering = ('comment_id',)
    list_display_links = ('comment_id', 'comment_content')
    search_fields = ('user_name', 'novel_title')

    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = '用户名'  # 设置列的标题

    def novel_title(self, obj):
        return obj.novel.novel_title
    novel_title.short_description = '小说名'  # 设置列的标题

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('chapter_id', 'chapter_title', 'short_content', 'novel_title')
    list_per_page = 15
    ordering = ('chapter_id',)
    list_display_links = ('chapter_id', 'chapter_title')
    search_fields = ('chapter_id', 'chapter_title')

    def novel_title(self, obj):
        return obj.novel.novel_title

    novel_title.short_description = '小说名'  # 设置列的标题

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    short_content.short_description = '内容'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')
    list_per_page = 15
    ordering = ('category_id',)
    list_display_links = ('category_id', 'category_name')
    search_fields = ('chapter_id', 'category_name')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('history_id', 'user_name', 'novel_title', 'chapter_title', 'history_time')
    readonly_fields = ('user_name', 'novel_title')  # 设置为只读
    exclude = ('user', 'novel')  # 在编辑表单中排除这两个字段
    list_per_page = 15
    ordering = ('history_id',)
    list_display_links = ('history_id',)
    search_fields = ('user_name', 'novel_title')

    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = '用户名'  # 设置列的标题

    def novel_title(self, obj):
        return obj.novel.novel_title
    novel_title.short_description = '小说名'  # 设置列的标题

    def chapter_title(self, obj):
        return obj.lastchapter.chapter_title
    chapter_title.short_description = '历史章节'  # 设置列的标题

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['lastchapter'].label_from_instance = lambda obj: f'{obj.chapter_title}'
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)




@admin.register(Cover)
class CoverAdmin(admin.ModelAdmin):
    list_display = ('cover_id', 'cover_link', 'state')
    list_per_page = 15
    ordering = ('cover_id',)
    list_display_links = ('cover_id', )
    search_fields = ('cover_id',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ('mail_id', 'user_name', 'content', 'mail_time')
    list_per_page = 15
    ordering = ('mail_id',)
    list_display_links = ('mail_id', )
    search_fields = ('mail_id',)

    raw_id_fields = ('user',)  # 设置 raw_id_fields 属性

    def user_name(self, obj):
        return obj.user.username

    user_name.short_description = '用户名'  # 设置列的标题
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

