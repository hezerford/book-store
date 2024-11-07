from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Genre name")
    description = models.TextField(blank=True, null=True, verbose_name="Descrition")

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["name"] 

class Book(models.Model):
    title = models.CharField(max_length=75, verbose_name="Заголовок")
    description = models.TextField(max_length=1500, verbose_name="Описание")
    author = models.CharField(max_length=100, verbose_name="Автор")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото аватара", blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    is_published = models.BooleanField(default=True, verbose_name="Активна на странице?")
    genre = models.ManyToManyField(Genre, verbose_name="Жанры")
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price with discount", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book-detail", kwargs={"book_slug": self.slug})

#   slugify преобразует пробелы в дефис и получается slug из названия
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['time_create', 'title']

class Quote(models.Model):
    quote = models.CharField(max_length=255, verbose_name="Цитата")
    author_quote = models.CharField(max_length=100, verbose_name="Автор цитаты")
    source = models.CharField(max_length=255, blank=True, null=True, verbose_name="Источник цитаты")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления цитаты")

    def __str__(self) -> str:
        return f"{self.author_quote}: {self.quote[:50]}..."

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
        ordering = ["-date_added"]

class Email(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    date_subscribed = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    last_sent = models.DateTimeField(blank=True, null=True, verbose_name='Дата последнего отправления')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Подписка на Email"
        verbose_name_plural = "Подписки на Email"
        ordering = ["-date_subscribed"]