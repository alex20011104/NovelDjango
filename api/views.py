import math

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
import json
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from api import models
from django.forms.models import model_to_dict
from django.utils import timezone
# import datetime
# from django.core import serializers

import pytz
# from datetime import datetime, timezone
from datetime import datetime
from django.utils import timezone
def time_since_last_read(last_read_time):
    now = datetime.now(timezone.utc)
    last_read_time = last_read_time.astimezone(timezone.utc)
    time_diff = now - last_read_time
    if time_diff.days > 0:
        return f"{time_diff.days} 天前读过"
    elif time_diff.seconds // 3600 > 0:
        return f"{time_diff.seconds // 3600} 小时前读过"
    elif time_diff.seconds // 60 > 0:
        return f"{time_diff.seconds // 60} 分钟前读过"
    else:
        return "刚刚读过"










#注册
def signup(request):
    user_id = request.GET.get('user_id')
    password = request.GET.get('password')
    username = request.GET.get('username')
    age = request.GET.get('age')
    gender = request.GET.get('gender')
    try:
        models.User.objects.get(user_id=user_id)
        return JsonResponse({'status': '400', 'message': '用户已存在'}, json_dumps_params={'ensure_ascii': False})
    except models.User.DoesNotExist:
        models.User.objects.create(user_id=user_id, password=password,username=username,gender=gender,age=age)
        return JsonResponse({'status': '200', 'message': '注册成功'}, json_dumps_params={'ensure_ascii': False})

# 登录
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.User
        fields=['user_id','username','gender','age','password']
@csrf_exempt
def login(request):

    if request.method == 'GET':
        # 解析请求数据
        user_id = str(request.GET.get('user_id'))
        password = str(request.GET.get('password'))  # 将密码参数值转换为字符串类型
        print(user_id, password)
        # 在数据库中查找用户
        try:
            user=models.User.objects.get(user_id=user_id)
            serializer = UserSerializer(user)
            # serialized_user = serializers.serialize('json', [user])
            # response_data = {
            #     'status': '200',
            #     'message': '查询用户信息成功',
            #     'user': serialized_user
            # }
            if user.password==password:
                # 匹配成功，返回成功响应
                return JsonResponse({'status': '200', 'message': '查询用户信息成功', 'user': serializer.data}, json_dumps_params={'ensure_ascii': False})
            else:
                # 匹配失败，返回错误响应
                return JsonResponse({'status': '400', 'message': '用户名或密码错误'}, json_dumps_params={'ensure_ascii': False})
        except models.User.DoesNotExist:
            # 没有找到用户，返回错误响应
            return JsonResponse({'status': '500', 'message': '用户不存在'}, json_dumps_params={'ensure_ascii': False})
    else:
        # 不支持其他请求方法，返回错误响应
        return JsonResponse({'status': 'error', 'message': '不支持该请求方法'}, json_dumps_params={'ensure_ascii': False})


# 更新用户信息
@csrf_exempt
def update_user(request):
        # 解析请求数据
        user_id = request.GET.get('user_id')
        username = request.GET.get('username')
        password = request.GET.get('password')
        gender = request.GET.get('gender')
        age = request.GET.get('age')
        age = int(age)
        print(user_id,username,password,gender,age)
        models.User.objects.filter(user_id=user_id).update(username=username,password=password,gender=gender,age=age)

        return JsonResponse({'status': '200', 'message': '更新成功'},json_dumps_params={'ensure_ascii': False})





 # 插入评论
@csrf_exempt
def insert_comment(request):
    user_id=request.POST.get('user_id')
    novel_id=request.POST.get('novel_id')
    comment=request.POST.get('comment')
    # timestamp=request.POST.get('timestamp')
    # if timestamp:
    #     comment_time = datetime.datetime.fromtimestamp(float(timestamp) / 1000)
    # else:
    #     return JsonResponse({"status": "error", "message": "Timestamp is missing"})       ,created_time=comment_time

    models.Comment.objects.create(user_id=user_id, novel_id=novel_id, comment_content=comment, created_time=timezone.now())
    return JsonResponse({'status': '200', 'message': '评论成功'}, json_dumps_params={'ensure_ascii': False})


# 显示评论
@csrf_exempt
def commentget(request):
    if request.method == 'GET':
        novel_id = request.GET.get('novel_id')
        comment = models.Comment.objects.filter(novel_id=novel_id).select_related('user')
        if not comment:
            return JsonResponse({'comment':[]}, safe=False, json_dumps_params={'ensure_ascii': False})

        # 将查询结果转换为包含小说名字的字典列表
        data = []
        for item in comment:
            formatted_created_time = timezone.localtime(item.created_time).strftime('%Y-%m-%d %H:%M')
            data.append({
                'comment_content':item.comment_content,
                'created_time':formatted_created_time,
                'username': item.user.username
            })

        return JsonResponse({'status': '200', 'message': '评论加载成功', 'comment': data},json_dumps_params={'ensure_ascii': False})
    else:
        # 不支持其他请求方法，返回错误响应
        return JsonResponse({'status': 'error', 'message': '不支持该请求方法'},json_dumps_params={'ensure_ascii': False})


#收藏提交
@csrf_exempt
def favorite(request):
    if request.method == 'POST':
        favorite = request.POST.get('favorite')
        user_id = request.POST.get('user_id')
        novel_id = request.POST.get('novel_id')
        #如果没有记录就插入
        try:
            user=models.Score.objects.get(user_id=user_id,novel_id=novel_id)
        except models.Score.DoesNotExist:
            models.Score.objects.create(user_id=user_id,novel_id=novel_id,favorite=favorite)
            return JsonResponse({'status': '200', 'message': '评分收藏插入成功'}, json_dumps_params={'ensure_ascii': False})
        # 更新信息
        models.Score.objects.filter(user_id=user_id,novel_id=novel_id).update(favorite=favorite)
        return JsonResponse({'status': '200', 'message': '评分收藏成功'},json_dumps_params={'ensure_ascii': False})
    else:
        # 不支持其他请求方法，返回错误响应
        return JsonResponse({'status': 'error', 'message': '不支持该请求方法'},json_dumps_params={'ensure_ascii': False})

#收藏展示
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Score
        fields = ['user_id','comment_id','comment_content','created_time','novel_id']
def favoriteget(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        novel_id = request.GET.get('novel_id')
        try:
            user = models.Score.objects.get(user_id=user_id, novel_id=novel_id)
        except models.Score.DoesNotExist:
            return JsonResponse({'status': '200', 'message': '没有记录', 'favorite': ''},json_dumps_params={'ensure_ascii': False})
        favorite = user.favorite
        return JsonResponse({'status': '200', 'message': '收藏记录获取成功', 'favorite': favorite },json_dumps_params={'ensure_ascii': False})
    else:
        # 不支持其他请求方法，返回错误响应
        return JsonResponse({'status': 'error', 'message': '不支持该请求方法'},json_dumps_params={'ensure_ascii': False})

#显示最新小说
def newnovels(request):

    novels = models.novel.objects.all().order_by('-pa_time')[:15]
    data = list(novels.values())
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

#显示全部小说
def allnovels(request):
    novels = models.novel.objects.all()
    data = list(novels.values())
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

#小说专题推荐
def  noveltopics(request):
    # 使用 filter 方法获取所有 state 为 1 的封面
    covers = models.Cover.objects.filter(state=1)

    # 创建一个列表来保存封面信息
    cover_list = []

    # 遍历查询结果，将每个封面的信息添加到列表中
    for cover in covers:
        cover_list.append({
            'cover_id': cover.cover_id,
            'cover_link': cover.cover_link,
        })


    return JsonResponse({'status': '200', 'message': '专题获取成功', 'cover_list': cover_list }, json_dumps_params={'ensure_ascii': False})

#邮件
def  Getmail(request):
    user_id = request.GET.get('user_id')
    # 使用 filter 方法获取所有 state 为 1 的封面
    mails = models.Mail.objects.filter(user_id=user_id)

    # 创建一个列表来保存封面信息
    mail_list = []

    # 遍历查询结果，将每个封面的信息添加到列表中
    for mail in mails:
        formatted_created_time = timezone.localtime(mail.mail_time).strftime('%Y-%m-%d %H:%M')
        mail_list.append({
            'mail_id': mail.mail_id,
            'content': mail.content,
            'mail_time': formatted_created_time
        })


    return JsonResponse({'status': '200', 'message': '邮件获取成功', 'mail_list': mail_list }, json_dumps_params={'ensure_ascii': False})


#获取小说详情
def novel_get(request):
    novel_id = request.GET.get('novel_id')
    novel = models.novel.objects.get(novel_id=novel_id)
    novel_dict = model_to_dict(novel)
    return JsonResponse({'status': '200', 'message': '小说获取成功', 'novel': novel_dict },json_dumps_params={'ensure_ascii': False})

# 获取小说目录
class ChapterGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chapter
        fields = ['chapter_id','chapter_title','novel_id']
def chapterGet(request):
    novel_id = request.GET.get('novel_id')
    chapter = models.Chapter.objects.filter(novel_id=novel_id).order_by('chapter_id')
    chapterlist = ChapterGetSerializer(chapter, many=True).data

    return JsonResponse({'status': '200', 'message': '章节获取成功', 'chapterlist': chapterlist },json_dumps_params={'ensure_ascii': False})

#根据章节ID获取章节内容
class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chapter
        fields = ['chapter_id','chapter_title','content','novel_id']
def contentGet(request):
    chapter_id = request.GET.get('chapter_id')
    content = models.Chapter.objects.get(chapter_id=chapter_id)
    chapter = ChapterSerializer(content).data
    return JsonResponse({'status': '200', 'message': '内容获取成功', 'chapter': chapter},json_dumps_params={'ensure_ascii': False})


#搜索小说
class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.novel
        fields = '__all__'
def search(requset):
    novel_title = requset.GET.get('novel_title')
    if not novel_title or novel_title.strip() == '':
        return JsonResponse([], safe=False, json_dumps_params={'ensure_ascii': False})
    novel = models.novel.objects.filter(novel_title__icontains=novel_title)
    serializer = SearchSerializer(novel,many=True).data
    return JsonResponse({'status': '200', 'message': '搜索成功', 'novel': serializer }, json_dumps_params={'ensure_ascii': False})

#书架展示
def bookshelf(request):
    user_id = request.GET.get('user_id')
    booklist = models.Score.objects.filter(user_id=user_id, favorite=1).select_related('novel') # 使用 select_related 获取相关的小说信息

    # 如果查询结果为空，直接返回空列表
    if not booklist:
        return JsonResponse([], safe=False, json_dumps_params={'ensure_ascii': False})

    # 将查询结果转换为包含小说名字的字典列表
    data = []
    for item in booklist:
        data.append({
            'favorite': item.favorite,
            'score': item.score,
            'user_id': item.user_id,
            'novel_id': item.novel.novel_id,
            'novel_title': item.novel.novel_title,
            'cover':item.novel.cover
        })

    return JsonResponse({'status': '200', 'message': '搜索成功', 'booklist': data }, safe=False, json_dumps_params={'ensure_ascii': False})

# 我的评论
def mycomment(request):
    user_id = request.GET.get('user_id')
    comment = models.Comment.objects.filter(user_id=user_id).select_related('user')

    # 如果查询结果为空，直接返回空列表
    if not comment:
        return JsonResponse([], safe=False, json_dumps_params={'ensure_ascii': False})
        # 将查询结果转换为包含小说名字的字典列表
    data = []
    for item in comment:
        formatted_created_time = timezone.localtime(item.created_time).strftime('%Y-%m-%d %H:%M')
        data.append({
            'comment_id':item.comment_id,
            'comment_content':item.comment_content,
            'created_time':formatted_created_time,
            'username':item.user.username
        })

    return JsonResponse({'status': '200', 'message': '我的评论加载成功', 'commentlist': data}, safe=False,json_dumps_params={'ensure_ascii': False})

#种类展示
def categoryget(request):
    categorylist = models.Category.objects.all()
    data = list(categorylist.values())
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

#展示某个种类的小说
def catenovel(request):
    category_id = request.GET.get('category_id')
    category = models.Category.objects.get(category_id=category_id)
    category_name = category.category_name
    categorynovel = models.novel.objects.filter(category=category_name)
    data = list(categorynovel.values())
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

# 用户历史记录提交
def historyup(request):
    user_id = request.GET.get('user_id')
    novel_id = request.GET.get('novel_id')
    lastchapter_id = request.GET.get('lastchapter_id')
    try:
        models.History.objects.get(user_id=user_id,novel_id=novel_id)
    except models.History.DoesNotExist:
        models.History.objects.create(user_id=user_id, novel_id=novel_id, lastchapter_id=lastchapter_id, history_time=timezone.now())
    models.History.objects.filter(user_id=user_id,novel_id=novel_id).update(lastchapter_id=lastchapter_id, history_time=timezone.now())
    return JsonResponse({'status': '200', 'message': '用户历史记录提交成功 '}, json_dumps_params={'ensure_ascii': False})

# 立即阅读
def read(request):
    user_id = request.GET.get('user_id')
    novel_id = request.GET.get('novel_id')
    history = models.History.objects.filter(user_id=user_id,novel_id=novel_id)
    if not history.exists():
        lastchapter = models.Chapter.objects.filter(novel_id=novel_id).first().chapter_id
        data ={
            'lastchapter_id': lastchapter,
        }
    else:
        lastchapter = history.first().lastchapter
        data = {
            'lastchapter_id': lastchapter.chapter_id,
        }
    return JsonResponse({'status': '200', 'message': '立即阅读信息成功', 'historyread': data}, safe=False, json_dumps_params={'ensure_ascii': False})


# 浏览记录展示
def myhistory(request):
    user_id = request.GET.get('user_id')
    history = models.History.objects.filter(user_id=user_id).select_related('lastchapter','novel')
    # 如果查询结果为空，直接返回空列表
    if not history:
        return JsonResponse([], safe=False, json_dumps_params={'ensure_ascii': False})
        # 将查询结果转换为包含小说名字的字典列表
    data = []
    for item in history:
        time_diff = time_since_last_read(item.history_time)
        data.append({
            'history_id': item.history_id,
            'history_time':time_diff,
            'user_id': item.user_id,
            'novel_id': item.novel_id,
            'novel_title': item.novel.novel_title,
            'novel_cover': item.novel.cover,
            'lastchapter_id': item.lastchapter_id,
            'lastchapter_name': item.lastchapter.chapter_title
        })

    return JsonResponse({'status': '200', 'message': '阅读记录加载成功', 'historylist': data}, safe=False,json_dumps_params={'ensure_ascii': False})

# 评分提交
def scoreup(request):
    user_id = request.GET.get('user_id')
    novel_id = request.GET.get('novel_id')
    score = request.GET.get('score')
    # 如果没有记录就插入
    try:
        models.Score.objects.get(user_id=user_id, novel_id=novel_id)
    except models.Score.DoesNotExist:
        models.Score.objects.create(user_id=user_id, novel_id=novel_id, score=score)
        return JsonResponse({'status': '200', 'message': '评分提交成功'}, json_dumps_params={'ensure_ascii': False})
    # 更新信息
    models.Score.objects.filter(user_id=user_id, novel_id=novel_id).update(score=score)
    return JsonResponse({'status': '200', 'message': '评分提交成功'}, json_dumps_params={'ensure_ascii': False})

# 获取评分
def getgrade(request):
    grade = 0
    ans = 0
    novel_id = request.GET.get('novel_id')
    Score = models.Score.objects.filter(novel_id=novel_id)
    for item in Score:
        if item.score is not None:
            grade += item.score
            ans += 1
    if ans == 0:
        return JsonResponse({'status': '200', 'message': '暂无评分信息','grade':'暂无评分'}, json_dumps_params={'ensure_ascii': False})
    grade = grade / ans
    rounded_grade = round(grade)  # 四舍五入后的评分
    return JsonResponse({'status': '200', 'message': '评分获取成功','grade':rounded_grade}, json_dumps_params={'ensure_ascii': False})

# 删除评论
def deletecomment(request):
    comment_id = request.GET.get('comment_id')
    try:
        comment = models.Comment.objects.get(comment_id=comment_id)
        comment.delete()
        return JsonResponse({'status': '200', 'message': '删除评分成功'}, json_dumps_params={'ensure_ascii': False})
    except models.Comment.DoesNotExist:
        return JsonResponse({'message': '评论不存在'})


from django.db.models import Avg
# 小说排名展示
def getrank(request):
    novels = models.novel.objects.annotate(avg_score=Avg('score__score')).order_by('-avg_score')
    data = []
    for novel in novels:
        avg_score = round(novel.avg_score, 1) if novel.avg_score is not None else "暂无评分"
        data.append({
            'novel_id' : novel.novel_id,
            'novel_title': novel.novel_title,
            'novel_cover': novel.cover,
            'author':novel.author,
            'category':novel.category,
            'score':avg_score
        })

    return JsonResponse({'status': '200', 'message': '排行榜加载成功', 'novelrank': data}, safe=False,json_dumps_params={'ensure_ascii': False})


# # 小说排名展示
# def getrank(request):
#     scores = models.Score.objects.order_by('-score').select_related('novel')
#     data = []
#     for item in scores:
#         data.append({
#             'novel_id' : item.novel_id,
#             'novel_title': item.novel.novel_title,
#             'novel_cover': item.novel.cover,
#             'author':item.novel.author,
#             'category':item.novel.category,
#             'score':item.score
#         })
#
#     return JsonResponse({'status': '200', 'message': '排行榜加载成功', 'novelrank': data}, safe=False,json_dumps_params={'ensure_ascii': False})

# 用户信息获取

def getuser(request):
    user_id = request.GET.get('user_id')
    user = models.User.objects.filter(user_id=user_id)
    data = list(user.values())
    return JsonResponse({'status': '200', 'message': '个人信息加载成功', 'user': data}, safe=False,json_dumps_params={'ensure_ascii': False})


# 获取我的评分

def getmygrade(request):
    user_id = request.GET.get('user_id')
    novel_id = request.GET.get('novel_id')
    mygrade = models.Score.objects.filter(user_id=user_id,novel_id=novel_id)
    if mygrade.exists():
        data = list(mygrade.values())
        mygrade_score = data[0]['score']
    else:
        mygrade_score = '还没评分'


    return JsonResponse({'status': '200', 'message': '我的评分加载成功', 'mygrade': mygrade_score}, safe=False, json_dumps_params={'ensure_ascii': False})

#获取我已经评分的小说
from django.db.models import Q

def getscorenovel(request):
    user_id = request.GET.get('user_id')
    scorenovel = models.Score.objects.filter(user_id=user_id).exclude(score__isnull=True).select_related('novel')
    data = []
    for item in scorenovel:
        data.append({
            'score_id':item.id,
            'novel_id': item.novel_id,
            'novel_title': item.novel.novel_title,
            'novel_cover': item.novel.cover,
            'author': item.novel.author,
            'category': item.novel.category,
            'score': item.score
        })
    print('a')
    return JsonResponse({'status': '200', 'message': '我的评分小说', 'scorenovel': data}, safe=False, json_dumps_params={'ensure_ascii': False})









# **************************************************************************************************************************
import numpy as np


def pearson_correlation(ratings1, ratings2):
    # 找到同时为这两部小说评分的用户
    common_ratings_mask = (ratings1 > 0) & (ratings2 > 0)

    # 根据上述掩码提取这两部小说的共同评分
    ratings1_common = ratings1[common_ratings_mask]
    ratings2_common = ratings2[common_ratings_mask]

    if len(ratings1_common) == 0:
        return 0

    # 计算这两部小说的平均评分
    ratings1_mean = np.mean(ratings1_common)
    ratings2_mean = np.mean(ratings2_common)

    # 计算皮尔逊相关系数的分子和分母
    numerator = np.sum((ratings1_common - ratings1_mean) * (ratings2_common - ratings2_mean))
    denominator = np.sqrt(np.sum((ratings1_common - ratings1_mean) ** 2) * np.sum((ratings2_common - ratings2_mean) ** 2))

    if denominator == 0:
        return 0

    # 计算皮尔逊相关系数
    return numerator / denominator


def handle(request):

    # 获取所有用户和小说
    users = {user.user_id: user for user in User.objects.all()}
    novel_dict = {novel_obj.novel_id: novel_obj for novel_obj in novel.objects.all()}


    user_id_request = request.GET.get('user_id')  # 获取请求中的用户ID

    # 初始化评分矩阵
    ratings_matrix = np.zeros((len(users), len(novel_dict)))
    # 填充评分矩阵
    for score_obj in Score.objects.all():
        user_index = list(users.keys()).index(score_obj.user_id)

        try:
            # 检查novel_dict字典中是否存在相应的小说ID
            novel_obj = score_obj.novel
            if novel_obj.novel_id not in novel_dict:
                print("Score对象引用的小说ID {} 不存在于novel_dict字典中。".format(novel_obj.novel_id))
                continue
        except novel.DoesNotExist:
            print("Score对象引用的小说不存在。")
            continue

        novel_index = list(novel_dict.keys()).index(novel_obj.novel_id)
        ratings_matrix[user_index, novel_index] = score_obj.score

    # 此时，ratings_matrix 是一个NumPy数组，其中行表示用户，列表示小说，数组中的每个元素表示用户对小说的评分。
    # 计算所有小说之间的皮尔逊相关系数矩阵
    num_novels = ratings_matrix.shape[1]
    pearson_matrix = np.zeros((num_novels, num_novels))
    for i in range(num_novels):
        for j in range(num_novels):
            pearson_matrix[i, j] = pearson_correlation(ratings_matrix[:, i], ratings_matrix[:, j])



    novel_dict_keys = list(novel_dict.keys())

    # 为每个用户生成推荐列表
    for user_index, user_ratings in enumerate(ratings_matrix):
        user_id = list(users.keys())[user_index]

        # 如果当前用户不是请求中的用户，则跳过
        if user_id != user_id_request:
            continue
        # 找到用户尚未评分的小说
        unrated_novels = np.where(user_ratings == 0)[0]


        # 计算这些未评分小说与用户已评分小说之间的相似度加权评分
        unrated_similarities = pearson_matrix[unrated_novels, :]
        user_rated_mask = user_ratings != 0
        weighted_scores = np.dot(unrated_similarities[:, user_rated_mask], user_ratings[user_rated_mask]) / np.sum(np.abs(unrated_similarities[:, user_rated_mask]), axis=1)

        # 根据加权评分对未评分小说进行排序，返回的是索引值
        recommended_novels = np.argsort(-weighted_scores)

        # 用于保存有效的推荐小说及其对应的加权评分
        valid_recommended_novels_and_scores = []

        # 遍历推荐的小说
        for novel_index in recommended_novels:
            # 检查这个小说是否在用户的未评分小说列表中，并且是否存在于 novel_dict
            if novel_dict_keys[unrated_novels[novel_index]] in novel_dict and unrated_novels[novel_index] in unrated_novels:
                # 如果是，那么保存这个小说的索引和加权评分
                valid_recommended_novels_and_scores.append((unrated_novels[novel_index], weighted_scores[novel_index]))

        # 创建一个新的推荐列表，只包含存在于 novel_dict_keys 中的索引值
        recommendations = []  # 修改为列表
        for i, score in valid_recommended_novels_and_scores:

            rnovel = novel_dict[novel_dict_keys[i]]
            if math.isnan(score):  # 检查score是否为NaN
                score = '未知'  # 如果是NaN，将其设置为None
            else:
                score = round(float(score), 2)  # 否则，保留两位小数
            recommendations.append({
                'novel_id': rnovel.novel_id,
                'novel_title': rnovel.novel_title,
                'novel_cover': rnovel.cover,
                'author': rnovel.author,
                'category': rnovel.category,
                'score': score
            })

    return JsonResponse({'status': '200', 'message': '推荐成功', 'recommendations': recommendations}, safe=False, json_dumps_params={'ensure_ascii': False})








import random
from api.models import novel, User, Score
def insertrandom(request):
    # 获取所有的novel和user对象
    all_novels = novel.objects.all()
    all_users = User.objects.all()

    # 设置插入评分的数量
    num_scores_to_insert = 100

    # 循环插入随机评分
    for _ in range(num_scores_to_insert):
        while True:
            # 从所有小说和用户中随机选择一个
            random_novel = random.choice(all_novels)
            random_user = random.choice(all_users)

            # 检查数据库中是否已经存在相同的用户和小说的评分记录
            existing_score = Score.objects.filter(user=random_user, novel=random_novel).first()

            # 如果不存在相同的记录，则跳出循环
            if existing_score is None:
                break

        # 生成一个1到10之间的随机评分
        random_score = random.randint(1, 10)

        # 创建一个Score对象并保存到数据库
        score_entry = Score(score=random_score, user=random_user, novel=random_novel)
        score_entry.save()
    return JsonResponse({'status': '200', 'message': '插入成功'}, safe=False, json_dumps_params={'ensure_ascii': False})



# # 打印小说相似度矩阵
    # similarity_matrix_decimal = np.round(pearson_matrix, 1)
    # print("小说相似度矩阵（皮尔逊相关系数）：")
    # print(similarity_matrix_decimal)


# # 根据加权评分对未评分小说进行排序
        # recommended_novels = np.argsort(-weighted_scores)
        #
        # # 创建一个新的推荐列表，只包含存在于 novel_dict_keys 中的索引值
        # # 并确保这些小说在用户的未评分小说列表中
        # valid_recommended_novels = [unrated_novels[i] for i in recommended_novels if novel_dict_keys[unrated_novels[i]] in novel_dict and unrated_novels[i] in unrated_novels]
        #
        # # 使用新的推荐列表来创建输出字符串，同时包含小说的加权分数
        # recommendations = {novel_dict[novel_dict_keys[i]].novel_title: weighted_scores[i] for i in valid_recommended_novels}
        # print("为用户{}推荐的小说及其对应的加权分数：".format(users[user_id].username), recommendations)



        # # 计算这些未评分小说与用户已评分小说之间的相似度加权评分
        # unrated_similarities = pearson_matrix[unrated_novels, :]
        # user_rated_mask = user_ratings != 0
        # weighted_scores = np.dot(unrated_similarities[:, user_rated_mask], user_ratings[user_rated_mask]) / np.sum(np.abs(unrated_similarities[:, user_rated_mask]), axis=1)
        #
        # # 根据加权评分对未评分小说进行排序
        # recommended_novels = np.argsort(-weighted_scores)
        #
        # # 创建一个新的推荐列表，只包含存在于 novel_dict_keys 中的索引值
        # # 并确保这些小说在用户的未评分小说列表中
        # valid_recommended_novels = [unrated_novels[i] for i in recommended_novels if novel_dict_keys[unrated_novels[i]] in novel_dict and unrated_novels[i] in unrated_novels]
        #
        # # 使用新的推荐列表来创建输出字符串
        # print("为用户{}推荐的小说：".format(users[user_id].username),[novel_dict[novel_dict_keys[i]].novel_title for i in valid_recommended_novels])


# # 计算这些未评分小说与用户已评分小说之间的相似度加权评分
        # weighted_scores = np.dot(pearson_matrix[unrated_novels, :], user_ratings) / np.sum(np.abs(pearson_matrix[unrated_novels, :]), axis=1)

# # 根据加权评分对未评分小说进行排序
        # recommended_novels = np.argsort(-weighted_scores)
        #
        # # 创建一个新的推荐列表，只包含存在于 novel_dict_keys 中的索引值
        # valid_recommended_novels = [i for i in recommended_novels if novel_dict_keys[i] in novel_dict]
        #
        # # 使用新的推荐列表来创建输出字符串
        # print("为用户{}推荐的小说：".format(users[user_id].username),[novel_dict[novel_dict_keys[i]].novel_title for i in valid_recommended_novels])


# import random
# from api.models import novel, User, Score
# def insertrandom(request):
#     # 获取所有的novel和user对象
#     all_novels = novel.objects.all()
#     all_users = User.objects.all()
#
#     # 为每个用户和每本小说插入一次随机评分
#     for user in all_users:
#         for novel_item in all_novels:
#             # 生成一个1到10之间的随机评分
#             random_score = random.randint(1, 10)
#             # 创建一个Score对象并保存到数据库
#             score_entry = Score(score=random_score, user=user, novel=novel_item)
#             score_entry.save()




# valid_recommended_novels = [i for i in recommended_novels if i < len(novel_dict_keys)]
        #
        # # 使用新的推荐列表来创建输出字符串
        # print("为用户{}推荐的小说：".format(users[user_id].username),[novel_dict[novel_dict_keys[i]].novel_title for i in valid_recommended_novels])

# print("为用户{}推荐的小说：".format(users[user_id].username),[novel_dict[novel_dict_keys[i]].novel_title for i in recommended_novels if i < len(novel_dict_keys)])

        # print("为用户{}推荐的小说：".format(users[user_id].username),[novel_dict[novel_dict_keys[i]].novel_title for i in recommended_novels])

        # # 输出推荐的小说列表
        # print("为用户{}推荐的小说：".format(users[user_id].username),[novel_dict[novel_dict_keys[i]].name for i in recommended_novels])
        #
        # print("为用户{}推荐的小说：".format(users[user_id].username), [novel_dict[i].name for i in recommended_novels])