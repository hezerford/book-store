from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Book, Genre, Quote
from user_profile.models import UserProfile
import random


class Command(BaseCommand):
    help = "Создает тестовые данные для приложения"

    def add_arguments(self, parser):
        parser.add_argument(
            "--books", type=int, default=20, help="Количество книг для создания"
        )
        parser.add_argument(
            "--users", type=int, default=5, help="Количество пользователей для создания"
        )

    def handle(self, *args, **options):
        self.stdout.write("Создание тестовых данных...")

        # Создаем жанры
        genres = self.create_genres()

        # Создаем книги
        books = self.create_books(genres, options["books"])

        # Создаем пользователей
        users = self.create_users(options["users"])

        # Создаем цитаты
        quotes = self.create_quotes()

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно создано: {len(books)} книг, {len(users)} пользователей, "
                f"{len(genres)} жанров, {len(quotes)} цитат"
            )
        )

    def create_genres(self):
        genres_data = [
            {"name": "Fiction", "description": "Художественная литература"},
            {"name": "Non-Fiction", "description": "Документальная литература"},
            {"name": "Science Fiction", "description": "Научная фантастика"},
            {"name": "Mystery", "description": "Детективы"},
            {"name": "Romance", "description": "Романтическая литература"},
            {"name": "Biography", "description": "Биографии"},
            {"name": "History", "description": "Историческая литература"},
            {"name": "Technology", "description": "Техническая литература"},
        ]

        genres = []
        for data in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=data["name"], defaults={"description": data["description"]}
            )
            genres.append(genre)
            if created:
                self.stdout.write(f"Создан жанр: {genre.name}")

        return genres

    def create_books(self, genres, count):
        titles = [
            "The Great Adventure",
            "Mystery of the Night",
            "Science and Discovery",
            "Love in Paris",
            "The Hidden Truth",
            "Future World",
            "Ancient Secrets",
            "Digital Revolution",
            "The Last Chapter",
            "Beyond the Stars",
            "City of Dreams",
            "The Lost Manuscript",
            "Quantum Mechanics",
            "Art of Programming",
            "Philosophy of Life",
            "The Time Machine",
            "War and Peace",
            "Pride and Prejudice",
            "1984",
            "Brave New World",
        ]

        authors = [
            "John Smith",
            "Jane Doe",
            "Robert Johnson",
            "Emily Brown",
            "Michael Wilson",
            "Sarah Davis",
            "David Miller",
            "Lisa Garcia",
            "James Rodriguez",
            "Maria Martinez",
            "Christopher Anderson",
            "Jennifer Taylor",
            "Daniel Thomas",
            "Amanda Jackson",
            "Matthew White",
            "Laura Harris",
            "Kevin Martin",
            "Nicole Thompson",
        ]

        books = []
        for i in range(count):
            title = random.choice(titles) + f" {i+1}"
            author = random.choice(authors)
            price = round(random.uniform(9.99, 49.99), 2)

            # 30% книг со скидкой
            discounted_price = None
            if random.random() < 0.3:
                discounted_price = round(price * random.uniform(0.6, 0.9), 2)

            book = Book.objects.create(
                title=title,
                author=author,
                description=f'Описание для книги "{title}" от автора {author}. '
                f"Это увлекательная история, которая захватит ваше внимание.",
                price=price,
                discounted_price=discounted_price,
                publication_year=random.randint(1990, 2024),
                pages=random.randint(200, 800),
                stock_quantity=random.randint(0, 50),
                isbn=f"978-{random.randint(100000, 999999)}-{random.randint(10, 99)}-{random.randint(1, 9)}",
            )

            # Добавляем случайные жанры
            book.genre.add(*random.sample(genres, random.randint(1, 3)))
            books.append(book)

            if i % 5 == 0:
                self.stdout.write(f"Создана книга: {book.title}")

        return books

    def create_users(self, count):
        users = []
        for i in range(count):
            username = f"user{i+1}"
            email = f"user{i+1}@example.com"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": f"User{i+1}",
                    "last_name": f"Test{i+1}",
                    "is_active": True,
                },
            )

            if created:
                user.set_password("testpass123")
                user.save()

                # Создаем профиль пользователя
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "city": random.choice(
                            ["Moscow", "St. Petersburg", "Novosibirsk", "Yekaterinburg"]
                        ),
                        "country": "Russia",
                        "phone_number": f"+7{random.randint(9000000000, 9999999999)}",
                    },
                )
                users.append(user)
                self.stdout.write(f"Создан пользователь: {user.username}")

        return users

    def create_quotes(self):
        quotes_data = [
            {
                "quote": "Книги - это корабли мысли, странствующие по волнам времени.",
                "author_quote": "Фрэнсис Бэкон",
                "source": "Опыты",
            },
            {
                "quote": "Чтение - это разговор с мудрецами, а письмо - разговор с глупцами.",
                "author_quote": "Фрэнсис Бэкон",
                "source": "Опыты",
            },
            {
                "quote": "Книга - это друг, который никогда не предаст.",
                "author_quote": "Джордж Элиот",
                "source": "Миддлмарч",
            },
            {
                "quote": "Хорошая книга - это подарок, который автор делает человечеству.",
                "author_quote": "Джозеф Аддисон",
                "source": "Зритель",
            },
            {
                "quote": "Книги - это зеркало души.",
                "author_quote": "Вирджиния Вулф",
                "source": "Своя комната",
            },
        ]

        quotes = []
        for data in quotes_data:
            quote, created = Quote.objects.get_or_create(
                quote=data["quote"],
                defaults={
                    "author_quote": data["author_quote"],
                    "source": data["source"],
                },
            )
            quotes.append(quote)
            if created:
                self.stdout.write(f"Создана цитата: {quote.author_quote}")

        return quotes
