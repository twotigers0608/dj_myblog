from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from mdeditor.fields import MDTextField


# 分类
class Category(models.Model):
    name = models.CharField(max_length=100)

    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tb_category'
        verbose_name = '分类'
        verbose_name_plural = verbose_name


# 标签
class Tag(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tb_tag'
        verbose_name = '标签'
        verbose_name_plural = verbose_name


# 文章
class Post(models.Model):
    # 标题
    title = models.CharField(max_length=70)
    # 内容
    # body = models.TextField()

    body = MDTextField()  # 注意为MDTextField()
    # 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt = models.CharField(max_length=200, blank=True)
    # 这两个列分别表示文章的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    # 标签
    tag = models.ManyToManyField(Tag, blank=True)
    # 分类
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # 作者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 阅读量
    views = models.PositiveIntegerField(default=0)

    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'tb_content'
        verbose_name = '文章内容'
        verbose_name_plural = verbose_name
        ordering = ['created_time', 'title']

    def __str__(self):
        return self.title


# 评论
class Comments(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    new_id = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_comments'
        verbose_name = '文章评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.text[:20]