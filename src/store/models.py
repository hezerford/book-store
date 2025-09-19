from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from decimal import Decimal

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class BookManager(models.Manager):
    """Менеджер для книг с дополнительными методами"""

    def with_ratings(self):
        """Получить книги с предварительно рассчитанным рейтингом"""
        from django.db.models import Avg, Count

        return self.annotate(
            average_rating=Avg("reviews__rating"), reviews_count=Count("reviews")
        )

    def published(self):
        """Только опубликованные книги"""
        return self.filter(is_published=True)

    def rated_high(self, min_rating=4.0):
        """Книги с высоким рейтингом"""
        return self.with_ratings().filter(average_rating__gte=min_rating)

    def popular(self, limit=10):
        """Популярные книги по количеству отзывов"""
        return self.with_ratings().order_by("-reviews_count")[:limit]


class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Genre name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.name:
            self.name = self.name.strip()
        super().clean()

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["name"]


class Book(models.Model):
    objects = BookManager()

    title = models.CharField(max_length=75, verbose_name="Заголовок")
    description = models.TextField(max_length=1500, verbose_name="Описание")
    author = models.CharField(max_length=100, verbose_name="Автор")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        validators=[
            MinValueValidator(Decimal("0.01"), message="Цена должна быть больше 0")
        ],
    )
    photo = ProcessedImageField(
        upload_to="book_covers/%Y/%m/%d/",
        processors=[ResizeToFill(800, 800)],
        format="JPEG",
        options={"quality": 85},
        verbose_name="Фото книги",
        blank=True,
        null=True,
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    is_published = models.BooleanField(default=True, verbose_name="Доступна к продаже?")
    genre = models.ManyToManyField(Genre, verbose_name="Жанры")
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Price with discount",
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                Decimal("0.01"), message="Скидочная цена должна быть больше 0"
            )
        ],
    )
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    # Новые поля для улучшения функциональности
    isbn = models.CharField(max_length=13, blank=True, null=True, verbose_name="ISBN")
    pages = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество страниц"
    )
    publication_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Год издания",
        validators=[
            MinValueValidator(1800, message="Год издания не может быть меньше 1800"),
            MaxValueValidator(
                2024, message="Год издания не может быть больше текущего года"
            ),
        ],
    )
    stock_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Количество на складе"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book-detail", kwargs={"book_slug": self.slug})

    def clean(self):
        """Валидация модели"""
        if self.title:
            self.title = self.title.strip()
        if self.author:
            self.author = self.author.strip()
        if self.description:
            self.description = self.description.strip()

        super().clean()

    def get_final_price(self):
        """Возвращает финальную цену с учетом скидки"""
        return self.discounted_price if self.discounted_price else self.price

    def get_discount_percentage(self):
        """Возвращает процент скидки"""
        if self.discounted_price and self.price:
            return round(((self.price - self.discounted_price) / self.price) * 100, 1)
        return 0

    def get_average_rating(self):
        """Рассчитывает средний рейтинг книги"""
        if self.reviews.exists():
            return self.reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return None

    def get_rating_display(self):
        """Форматированное отображение рейтинга"""
        avg_rating = self.get_average_rating()
        if avg_rating is not None:
            return f"{avg_rating:.1f}/5.0 ⭐"
        return "Нет оценок"

    #   slugify преобразует пробелы в дефис и получается slug из названия
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Нормализуем денежные значения до 2 знаков после запятой
        if self.price is not None:
            self.price = (Decimal(self.price)).quantize(Decimal("0.01"))
        if self.discounted_price is not None:
            self.discounted_price = (Decimal(self.discounted_price)).quantize(
                Decimal("0.01")
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ["time_create", "title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["price"]),
            models.Index(fields=["discounted_price"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="discounted_lt_price_or_null",
                condition=Q(discounted_price__isnull=True)
                | Q(discounted_price__lt=models.F("price")),
            )
        ]


class Quote(models.Model):
    quote = models.CharField(max_length=255, verbose_name="Цитата")
    author_quote = models.CharField(max_length=100, verbose_name="Автор цитаты")
    source = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Источник цитаты"
    )
    date_added = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления цитаты"
    )

    def __str__(self) -> str:
        return f"{self.author_quote}: {self.quote[:50]}..."

    def clean(self):
        if self.quote:
            self.quote = self.quote.strip()
        if self.author_quote:
            self.author_quote = self.author_quote.strip()
        if self.source:
            self.source = self.source.strip()
        super().clean()

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
        ordering = ["-date_added"]


class Subscription(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    date_subscribed = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата подписки"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    last_sent = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата последнего отправления"
    )

    def __str__(self):
        return self.email

    def clean(self):
        if self.email:
            self.email = self.email.lower().strip()
        super().clean()

    class Meta:
        verbose_name = "Подписка на Email"
        verbose_name_plural = "Подписки на Email"
        ordering = ["-date_subscribed"]
