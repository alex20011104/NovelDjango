# Create your models here.
from django.db import models
from django.utils import timezone
# Create your models here.
class novel(models.Model):
    class Meta:
        db_table='novel'
        verbose_name_plural = '小说'

    novel_id = models.AutoField(primary_key=True, verbose_name=u'小说ID')
    novel_title=models.CharField(max_length=255, verbose_name=u'小说名')
    author=models.CharField(max_length=255, verbose_name=u'作者')
    description=models.CharField(max_length=1023, verbose_name=u'简介')
    cover=models.CharField(max_length=1023, verbose_name=u'封面')
    category=models.CharField(max_length=255, verbose_name=u'种类')
    state = models.CharField(max_length=20, null=True, verbose_name=u'状态')
    novellist = models.CharField(max_length=1023, verbose_name=u'爬取地址')
    pa_time = models.DateTimeField(default=None, null=True, verbose_name=u'爬取时间')
    pa_state = models.IntegerField(default=0, verbose_name=u'爬取状态')

class User(models.Model):
    class Meta:
        db_table='user'
        verbose_name_plural = '读者'

    user_id=models.CharField(primary_key=True, max_length=255, verbose_name=u'用户ID')
    username=models.CharField(max_length=255, verbose_name=u'昵称')
    password=models.CharField(max_length=255, verbose_name=u'密码')
    gender=models.CharField(max_length=255, null=True, verbose_name=u'性别')
    age=models.IntegerField(null=True, verbose_name=u'年龄')

class Score(models.Model):
    class Meta:
        db_table='score'
        verbose_name_plural = '收藏评分'

    id = models.AutoField(primary_key=True, verbose_name=u'ID')
    favorite = models.IntegerField(null=True, verbose_name=u'收藏')
    score = models.IntegerField(null=True, default=8, verbose_name=u'评分')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel = models.ForeignKey(novel, on_delete=models.CASCADE)  # 添加一个外键字段，连接 novel 表

class Comment(models.Model):
    class Meta:
        db_table='comment'
        verbose_name_plural = '评论'

    comment_id=models.AutoField(primary_key=True, verbose_name=u'评论ID')
    comment_content=models.CharField(max_length=1023, verbose_name=u'评论内容')
    created_time=models.DateTimeField(verbose_name=u'评论时间')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # user_id=models.CharField(max_length=255)
    novel = models.ForeignKey(novel, on_delete=models.CASCADE)



class Chapter(models.Model):
    class Meta:
        db_table = 'chapter'
        verbose_name_plural = '章节'

    chapter_id = models.AutoField(primary_key=True, verbose_name=u'章节ID')
    chapter_title = models.CharField(max_length=255, verbose_name=u'章节名')
    content = models.TextField(verbose_name=u'内容')
    novel = models.ForeignKey(novel, on_delete=models.CASCADE)

class Category(models.Model):
    class Meta:
        db_table = 'category'
        verbose_name_plural = '种类'

    category_id = models.AutoField(primary_key=True, verbose_name=u'种类ID')
    category_name = models.CharField(max_length=255, verbose_name=u'种类')

class History(models.Model):
    class Meta:
        db_table = 'history'
        verbose_name_plural = '阅读历史'

    history_id = models.AutoField(primary_key=True, verbose_name=u'历史记录ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel =models.ForeignKey(novel, on_delete=models.CASCADE)
    lastchapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, to_field='chapter_id')
    history_time = models.DateTimeField(verbose_name=u'历史时间')

    # lastchapter_id = models.IntegerField()



class Cover(models.Model):
    class Meta:
        db_table = 'cover'
        verbose_name_plural = '推荐专题'

    cover_id  = models.AutoField(primary_key=True, verbose_name=u'封面ID')
    cover_link = models.CharField(max_length=1023, verbose_name=u'封面网址')
    state = models.IntegerField(default=0, verbose_name=u'推送状态')

class Mail(models.Model):
    class Meta:
        db_table = 'mail'
        verbose_name_plural = '邮件'

    mail_id = models.AutoField(primary_key=True, verbose_name=u'邮箱ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=1023, verbose_name=u'邮件内容')
    mail_time = models.DateTimeField(verbose_name=u'邮件时间')