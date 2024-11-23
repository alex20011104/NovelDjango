"""djangoDemo1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path,include
from api import views
from api.views import allnovels,login,update_user,insert_comment,commentget,favorite,favoriteget,novel_get,chapterGet,contentGet,search,signup,bookshelf,mycomment,categoryget,catenovel,historyup,read,myhistory,scoreup,getgrade,deletecomment,getrank,getuser,handle,getmygrade,insertrandom,getscorenovel,noveltopics,Getmail,newnovels

admin.site.site_header = "微信小说阅读管理系统 "  # Django administration 替换为 小说管理
admin.site.site_title = "微信小说阅读管理系统"  # Django site admin 替换为 小说管理
admin.site.index_title = "微信小说阅读管理系统"  # Site administration 替换为 小说管理系统
urlpatterns = [
    path('admin/', admin.site.urls),
    path('allnovels/', allnovels),
    path('login/', login),
    path('update_user/', update_user),
    path('commentup/', insert_comment),
    path('comment/',commentget),
    path('favorite/',favorite),
    path('favoriteget/',favoriteget),
    path('novel_get/',novel_get),
    path('chapterGet/',chapterGet),
    path('contentGet/',contentGet),
    path('search/',search),
    path('signup/',signup),
    path('bookshelf/',bookshelf),
    path('mycomment/',mycomment),
    path('categoryget/',categoryget),
    path('catenovel/',catenovel),
    path('historyup/',historyup),
    path('read/',read),
    path('myhistory/',myhistory),
    path('scoreup/',scoreup),
    path('getgrade/',getgrade),
    path('deletecomment/',deletecomment),
    path('getrank/',getrank),
    path('getuser/',getuser),
    # 推荐
    path('handle/',handle),

    path('getmygrade/',getmygrade),
    # 随机插入
    path('insertrandom/',insertrandom),
    path('getscorenovel/',getscorenovel),
    path('noveltopics/',noveltopics),
    path('Getmail/',Getmail),
    path('newnovels/',newnovels),

    # path('api/',views.LoginViews.as_view()),
    # path('api/', include('api.urls')),

]
