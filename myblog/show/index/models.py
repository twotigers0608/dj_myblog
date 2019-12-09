# Create your models here.
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from mdeditor.fields import MDTextField
from django.utils.html import strip_tags
import markdown


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
    created_time = models.DateTimeField(default=timezone.now)
    modified_time = models.DateTimeField()
    # 标签
    tag = models.ManyToManyField(Tag, blank=True)
    # 分类
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # 作者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 阅读量
    views = models.PositiveIntegerField(default=0, editable=False)

    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数
    def __str__(self):
        return self.title

    #返回 id
    def get_absolute_url(self):
        return reverse('index:article', kwargs={'pk': self.pk})

    #阅读数自动 +1
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()

        # 首先实例化一个 Markdown 类，用于渲染 body 的文本。
        # 由于摘要并不需要生成文章目录，所以去掉了目录拓展。
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])

        # 先将 Markdown 文本渲染成 HTML 文本
        # strip_tags 去掉 HTML 文本的全部 HTML 标签
        # 从文本摘取前 54 个字符赋给 excerpt
        self.excerpt = strip_tags(md.convert(self.body))[:54]

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'tb_content'
        verbose_name = '文章内容'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']



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
