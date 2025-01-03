# Generated by Django 4.1.7 on 2023-05-20 13:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_novel_pa_state_novel_pa_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='novellist',
            field=models.CharField(default='', max_length=1023, verbose_name='爬取地址'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 20, 13, 34, 19, tzinfo=datetime.timezone.utc), verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='history',
            name='history_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 20, 13, 34, 19, tzinfo=datetime.timezone.utc), verbose_name='历史时间'),
        ),
        migrations.AlterField(
            model_name='novel',
            name='pa_time',
            field=models.DateTimeField(default=None, verbose_name='爬取时间'),
        ),
    ]
