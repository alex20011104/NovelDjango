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


from django.core.management.base import BaseCommand
from api.models import Score, User, novel
import numpy as np


class Command(BaseCommand):
    help = 'Generate novel recommendations based on Pearson Correlation Coefficient'

    def handle(self, *args, **options):
        # 获取所有用户和小说
        users = User.objects.all()
        novels = novel.objects.all()

        # 初始化评分矩阵
        ratings_matrix = np.zeros((len(users), len(novels)))

        # 填充评分矩阵
        for score_obj in Score.objects.all():
            user_index = users.index(score_obj.user)
            novel_index = novels.index(score_obj.novel)
            ratings_matrix[user_index, novel_index] = score_obj.score

        # 此时，ratings_matrix 是一个NumPy数组，其中行表示用户，列表示小说，数组中的每个元素表示用户对小说的评分。

        # ... 之前的代码 ...

        # 计算所有小说之间的皮尔逊相关系数矩阵
        num_novels = ratings_matrix.shape[1]
        pearson_matrix = np.zeros((num_novels, num_novels))

        for i in range(num_novels):
            for j in range(num_novels):
                pearson_matrix[i, j] = pearson_correlation(ratings_matrix[:, i], ratings_matrix[:, j])

        # 为每个用户生成推荐列表
        for user_id, user_ratings in enumerate(ratings_matrix):
            # 找到用户尚未评分的小说
            unrated_novels = np.where(user_ratings == 0)[0]

            # 计算这些未评分小说与用户已评分小说之间的相似度加权评分
            weighted_scores = np.dot(pearson_matrix[unrated_novels, :], user_ratings) / np.sum(np.abs(pearson_matrix[unrated_novels, :]), axis=1)

            # 根据加权评分对未评分小说进行排序
            recommended_novels = np.argsort(-weighted_scores)

            # 输出推荐的小说列表
            print("为用户{}推荐的小说：".format(users[user_id].username), [novels[i].novel])
