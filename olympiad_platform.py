"""
===========================================================
🏆 ОЛИМПИАДНАЯ ПЛАТФОРМА - ПОЛНЫЙ КОД В ОДНОМ ФАЙЛЕ
===========================================================

Этот файл содержит полностью рабочую олимпиадную платформу на Django.
Все компоненты (модели, представления, шаблоны) находятся здесь.

КАК ЗАПУСТИТЬ:
1. pip install django
2. python olympiad_platform.py migrate
3. python olympiad_platform.py runserver
4. Открыть http://127.0.0.1:8000/
"""

# ============================================================================
# ИМПОРТЫ
# ============================================================================
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь Python
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Django должен быть установлен заранее
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'olympiad_platform.settings')

# Импорты Django
from django import setup
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Template, Context
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json
import hashlib
import random
import math

# ============================================================================
# КОНФИГУРАЦИЯ DJANGO
# ============================================================================

if not settings.configured:
    settings.configure(
        # Основные настройки
        DEBUG=True,
        SECRET_KEY='django-insecure-olympiad-platform-secret-key-2024',
        ALLOWED_HOSTS=['localhost', '127.0.0.1'],

        # Приложения
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'olympiad_platform',
        ],

        # База данных (SQLite для простоты)
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        },

        # Middleware
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],

        # Аутентификация
        AUTH_USER_MODEL='olympiad_platform.User',

        # Шаблоны
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],

        # URL
        ROOT_URLCONF='olympiad_platform',

        # Локализация
        LANGUAGE_CODE='ru-ru',
        TIME_ZONE='Europe/Moscow',
        USE_I18N=True,
        USE_TZ=True,

        # Статические файлы
        STATIC_URL='static/',

        # Настройки для разработки
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

    # Инициализируем Django
    setup()


# ============================================================================
# МОДЕЛИ (MODELS)
# ============================================================================

class UserManager(BaseUserManager):
    """Менеджер пользователей"""

    def create_user(self, username, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
    Расширяем стандартную модель Django для олимпиадной платформы
    """
    # Базовые поля (уже есть в AbstractUser): username, email, password, first_name, last_name

    # Дополнительные поля для рейтинговой системы
    elo_rating = models.IntegerField(
        default=1000,
        verbose_name="Рейтинг Elo",
        help_text="Рейтинг игрока по системе Elo"
    )

    # Статистика
    total_matches = models.IntegerField(default=0, verbose_name="Всего матчей")
    wins = models.IntegerField(default=0, verbose_name="Побед")
    losses = models.IntegerField(default=0, verbose_name="Поражений")
    draws = models.IntegerField(default=0, verbose_name="Ничьих")
    streak = models.IntegerField(default=0, verbose_name="Серия побед/поражений")

    # Прогресс
    total_solved = models.IntegerField(default=0, verbose_name="Всего решено задач")
    total_points = models.IntegerField(default=0, verbose_name="Всего баллов")

    # Метки времени
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Последняя активность")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-elo_rating']

    def __str__(self):
        return f"{self.username} ({self.elo_rating})"

    def update_stats_after_match(self, result, points=0):
        """
        ОБНОВЛЕНИЕ СТАТИСТИКИ ПОСЛЕ МАТЧА

        result: 'win', 'loss', 'draw'
        points: начисленные баллы за решение задачи
        """
        self.total_matches += 1

        if result == 'win':
            self.wins += 1
            self.streak = max(0, self.streak) + 1
        elif result == 'loss':
            self.losses += 1
            self.streak = min(0, self.streak) - 1
        elif result == 'draw':
            self.draws += 1

        if points > 0:
            self.total_points += points
            self.total_solved += 1

        self.save()

    def calculate_win_rate(self):
        """РАСЧЕТ ПРОЦЕНТА ПОБЕД"""
        if self.total_matches == 0:
            return 0
        return round((self.wins / self.total_matches) * 100, 2)

    def get_rank(self):
        """ОПРЕДЕЛЕНИЕ РАНГА ПО РЕЙТИНГУ"""
        if self.elo_rating >= 2000:
            return "Гроссмейстер 👑"
        elif self.elo_rating >= 1800:
            return "Мастер 🎯"
        elif self.elo_rating >= 1600:
            return "Эксперт ⭐"
        elif self.elo_rating >= 1400:
            return "Продвинутый 🔥"
        elif self.elo_rating >= 1200:
            return "Средний 💪"
        else:
            return "Новичок 🐣"

    def get_streak_emoji(self):
        """ПОЛУЧЕНИЕ ЭМОДЗИ ДЛЯ СЕРИИ"""
        if self.streak > 0:
            return "🔥" * min(self.streak, 3)
        elif self.streak < 0:
            return "😢"
        return "➖"


class Subject(models.Model):
    """
    МОДЕЛЬ ПРЕДМЕТА
    Например: Математика, Информатика, Физика
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon = models.CharField(max_length=50, default="📚", verbose_name="Иконка")

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"

    def get_task_count(self):
        """КОЛИЧЕСТВО ЗАДАЧ ПО ПРЕДМЕТУ"""
        return Task.objects.filter(subject=self).count()


class Task(models.Model):
    """
    МОДЕЛЬ ЗАДАЧИ
    Основная сущность платформы - олимпиадная задача
    """
    # Уровни сложности
    DIFFICULTY_EASY = 'easy'
    DIFFICULTY_MEDIUM = 'medium'
    DIFFICULTY_HARD = 'hard'
    DIFFICULTY_EXPERT = 'expert'

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, 'Легкая 🟢'),
        (DIFFICULTY_MEDIUM, 'Средняя 🟡'),
        (DIFFICULTY_HARD, 'Сложная 🔴'),
        (DIFFICULTY_EXPERT, 'Эксперт ⚫'),
    ]

    # Типы задач
    TYPE_SINGLE = 'single'
    TYPE_MULTIPLE = 'multiple'
    TYPE_TEXT = 'text'
    TYPE_CODE = 'code'

    TYPE_CHOICES = [
        (TYPE_SINGLE, 'Один верный ответ'),
        (TYPE_MULTIPLE, 'Несколько верных ответов'),
        (TYPE_TEXT, 'Текстовый ответ'),
        (TYPE_CODE, 'Программный код'),
    ]

    # Основные поля
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Условие задачи")

    # Классификация
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Предмет"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default=DIFFICULTY_MEDIUM,
        verbose_name="Сложность"
    )
    task_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_SINGLE,
        verbose_name="Тип задачи"
    )

    # Оценка
    points = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Баллы"
    )

    # Проверка
    correct_answer = models.TextField(verbose_name="Правильный ответ")
    explanation = models.TextField(blank=True, verbose_name="Объяснение решения")

    # Метаданные
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_tasks',
        verbose_name="Автор"
    )
    is_public = models.BooleanField(default=True, verbose_name="Опубликована")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    # Статистика
    total_attempts = models.IntegerField(default=0, verbose_name="Всего попыток")
    successful_attempts = models.IntegerField(default=0, verbose_name="Успешных попыток")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'difficulty']),
            models.Index(fields=['is_public', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

    def save(self, *args, **kwargs):
        """ПЕРЕОПРЕДЕЛЕНИЕ СОХРАНЕНИЯ"""
        if not self.author and hasattr(self, '_current_user'):
            self.author = self._current_user
        super().save(*args, **kwargs)

    def success_rate(self):
        """ПРОЦЕНТ УСПЕШНЫХ РЕШЕНИЙ"""
        if self.total_attempts == 0:
            return 0
        return round((self.successful_attempts / self.total_attempts) * 100, 2)

    def get_difficulty_color(self):
        """ЦВЕТ ДЛЯ ОТОБРАЖЕНИЯ СЛОЖНОСТИ"""
        colors = {
            'easy': 'success',
            'medium': 'warning',
            'hard': 'danger',
            'expert': 'dark',
        }
        return colors.get(self.difficulty, 'secondary')

    def check_answer(self, user_answer):
        """
        ПРОВЕРКА ОТВЕТА ПОЛЬЗОВАТЕЛЯ

        user_answer: ответ пользователя (строка или список)
        возвращает: (is_correct, message)
        """
        self.total_attempts += 1

        # Приводим к нижнему регистру для сравнения
        correct = str(self.correct_answer).strip().lower()
        user = str(user_answer).strip().lower()

        is_correct = (correct == user)

        if is_correct:
            self.successful_attempts += 1
            message = "✅ Верно! Отличная работа!"
        else:
            message = f"❌ Неверно. Правильный ответ: {self.correct_answer}"

        self.save()

        return is_correct, message

    def get_similar_tasks(self, limit=3):
        """ПОЛУЧЕНИЕ ПОХОЖИХ ЗАДАЧ"""
        return Task.objects.filter(
            subject=self.subject,
            difficulty=self.difficulty,
            is_public=True
        ).exclude(id=self.id).order_by('?')[:limit]


class Solution(models.Model):
    """
    МОДЕЛЬ РЕШЕНИЯ
    Сохраняет попытки пользователей решить задачи
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solutions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')

    # Решение
    answer = models.TextField(verbose_name="Ответ пользователя")
    is_correct = models.BooleanField(default=False, verbose_name="Правильно")

    # Время и производительность
    time_spent = models.IntegerField(default=0, verbose_name="Затраченное время (сек)")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")

    # Дополнительно
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")

    class Meta:
        verbose_name = "Решение"
        verbose_name_plural = "Решения"
        ordering = ['-submitted_at']
        unique_together = [['user', 'task']]  # Одна попытка на задачу (можно изменить)

    def __str__(self):
        status = "✅" if self.is_correct else "❌"
        return f"{status} {self.user.username} -> {self.task.title}"


class PvPMatch(models.Model):
    """
    МОДЕЛЬ PvP МАТЧА
    Соревнование между двумя игроками
    """
    STATUS_WAITING = 'waiting'
    STATUS_ACTIVE = 'active'
    STATUS_FINISHED = 'finished'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_WAITING, 'Ожидание игроков'),
        (STATUS_ACTIVE, 'Идет матч'),
        (STATUS_FINISHED, 'Завершен'),
        (STATUS_CANCELLED, 'Отменен'),
    ]

    # Игроки и задача
    player1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_player1'
    )
    player2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_player2',
        null=True,
        blank=True
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='pvp_matches'
    )

    # Ответы
    player1_answer = models.TextField(blank=True, verbose_name="Ответ игрока 1")
    player2_answer = models.TextField(blank=True, verbose_name="Ответ игрока 2")

    # Результаты
    player1_correct = models.BooleanField(null=True, blank=True, verbose_name="Игрок 1 прав")
    player2_correct = models.BooleanField(null=True, blank=True, verbose_name="Игрок 2 прав")

    # Время
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING,
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Начало")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Окончание")

    # Рейтинг
    player1_rating_before = models.IntegerField(default=1000, verbose_name="Рейтинг игрока 1 до")
    player2_rating_before = models.IntegerField(default=1000, verbose_name="Рейтинг игрока 2 до")
    player1_rating_change = models.IntegerField(default=0, verbose_name="Изменение рейтинга игрока 1")
    player2_rating_change = models.IntegerField(default=0, verbose_name="Изменение рейтинга игрока 2")

    # Уникальный идентификатор
    match_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Код матча"
    )

    class Meta:
        verbose_name = "PvP матч"
        verbose_name_plural = "PvP матчи"
        ordering = ['-created_at']

    def __str__(self):
        players = f"{self.player1.username} vs {self.player2.username if self.player2 else '?'}"
        return f"{self.match_code}: {players} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """СОЗДАНИЕ УНИКАЛЬНОГО КОДА ПРИ СОЗДАНИИ"""
        if not self.match_code:
            self.match_code = self.generate_match_code()
        if not self.player1_rating_before:
            self.player1_rating_before = self.player1.elo_rating
        if self.player2 and not self.player2_rating_before:
            self.player2_rating_before = self.player2.elo_rating

        super().save(*args, **kwargs)

    def generate_match_code(self):
        """ГЕНЕРАЦИЯ УНИКАЛЬНОГО КОДА МАТЧА"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def start_match(self, player2=None):
        """НАЧАЛО МАТЧА"""
        if player2:
            self.player2 = player2
            self.player2_rating_before = player2.elo_rating

        self.status = self.STATUS_ACTIVE
        self.started_at = timezone.now()
        self.save()

    def submit_answer(self, player, answer):
        """
        ОТПРАВКА ОТВЕТА ИГРОКОМ

        player: 1 или 2 (номер игрока)
        answer: ответ пользователя
        """
        if player == 1:
            self.player1_answer = answer
            self.player1_correct = self.check_answer(answer)
        elif player == 2:
            self.player2_answer = answer
            self.player2_correct = self.check_answer(answer)

        self.save()

        # Проверяем, завершен ли матч
        if self.player1_answer and self.player2_answer:
            self.finish_match()

    def check_answer(self, answer):
        """ПРОВЕРКА ОТВЕТА"""
        correct = str(self.task.correct_answer).strip().lower()
        user = str(answer).strip().lower()
        return correct == user

    def finish_match(self):
        """ЗАВЕРШЕНИЕ МАТЧА И ПОДСЧЕТ РЕЗУЛЬТАТОВ"""
        if self.status != self.STATUS_ACTIVE:
            return

        self.status = self.STATUS_FINISHED
        self.finished_at = timezone.now()

        # Подсчитываем результаты
        self.calculate_results()

        # Обновляем статистику игроков
        self.update_player_stats()

        self.save()

    def calculate_results(self):
        """ПОДСЧЕТ РЕЗУЛЬТАТОВ И ИЗМЕНЕНИЯ РЕЙТИНГА"""
        # Используем систему Elo для расчета изменений рейтинга
        k_factor = 32  # Коэффициент K в системе Elo

        # Ожидаемые результаты
        expected1 = 1 / (1 + 10 ** ((self.player2_rating_before - self.player1_rating_before) / 400))
        expected2 = 1 - expected1

        # Фактические результаты
        if self.player1_correct and not self.player2_correct:
            actual1, actual2 = 1, 0
            result = "player1_win"
        elif not self.player1_correct and self.player2_correct:
            actual1, actual2 = 0, 1
            result = "player2_win"
        elif self.player1_correct and self.player2_correct:
            actual1, actual2 = 0.5, 0.5
            result = "draw"
        else:
            actual1, actual2 = 0, 0
            result = "both_lose"

        # Рассчитываем изменения рейтинга
        self.player1_rating_change = round(k_factor * (actual1 - expected1))
        self.player2_rating_change = round(k_factor * (actual2 - expected2))

        # Обновляем рейтинги игроков
        self.player1.elo_rating += self.player1_rating_change
        self.player2.elo_rating += self.player2_rating_change
        self.player1.save()
        self.player2.save()

        return result

    def update_player_stats(self):
        """ОБНОВЛЕНИЕ СТАТИСТИКИ ИГРОКОВ ПОСЛЕ МАТЧА"""
        result = "draw"

        if self.player1_rating_change > 0:
            self.player1.update_stats_after_match('win', self.task.points)
            self.player2.update_stats_after_match('loss')
            result = "player1_win"
        elif self.player2_rating_change > 0:
            self.player1.update_stats_after_match('loss')
            self.player2.update_stats_after_match('win', self.task.points)
            result = "player2_win"
        else:
            self.player1.update_stats_after_match('draw')
            self.player2.update_stats_after_match('draw')

        return result

    def get_winner(self):
        """ПОЛУЧЕНИЕ ПОБЕДИТЕЛЯ"""
        if self.player1_correct and not self.player2_correct:
            return self.player1
        elif not self.player1_correct and self.player2_correct:
            return self.player2
        elif self.player1_correct and self.player2_correct:
            return "draw"  # Ничья
        else:
            return None  # Оба проиграли


class MatchmakingQueue:
    """
    КЛАСС ДЛЯ MATCHMAKING (ПОДБОРА СОПЕРНИКОВ)
    В реальном проекте использовался бы Redis, здесь используем память
    """
    _queue = []
    _active_matches = {}

    @classmethod
    def add_player(cls, player, rating):
        """ДОБАВЛЕНИЕ ИГРОКА В ОЧЕРЕДЬ"""
        # Проверяем, не в очереди ли уже
        for p in cls._queue:
            if p['player'].id == player.id:
                return p

        queue_entry = {
            'player': player,
            'rating': rating,
            'joined_at': timezone.now(),
            'match_id': None
        }
        cls._queue.append(queue_entry)

        # Пытаемся найти соперника
        cls.try_matchmaking()

        return queue_entry

    @classmethod
    def remove_player(cls, player):
        """УДАЛЕНИЕ ИГРОКА ИЗ ОЧЕРЕДИ"""
        cls._queue = [p for p in cls._queue if p['player'].id != player.id]

    @classmethod
    def try_matchmaking(cls):
        """ПОПЫТКА НАЙТИ СОПЕРНИКА"""
        if len(cls._queue) < 2:
            return None

        # Сортируем по рейтингу и времени ожидания
        sorted_queue = sorted(cls._queue, key=lambda x: x['rating'])

        # Ищем пары с близким рейтингом
        for i in range(len(sorted_queue) - 1):
            player1 = sorted_queue[i]
            player2 = sorted_queue[i + 1]

            # Разница в рейтинге должна быть не больше 200
            if abs(player1['rating'] - player2['rating']) <= 200:
                # Нашли пару!
                return cls.create_match(player1, player2)

        return None

    @classmethod
    def create_match(cls, player1_entry, player2_entry):
        """СОЗДАНИЕ МАТЧА"""
        # Выбираем случайную задачу средней сложности
        task = Task.objects.filter(
            difficulty=Task.DIFFICULTY_MEDIUM,
            is_public=True
        ).order_by('?').first()

        if not task:
            task = Task.objects.filter(is_public=True).first()

        # Создаем матч
        match = PvPMatch.objects.create(
            player1=player1_entry['player'],
            player2=player2_entry['player'],
            task=task,
            status=PvPMatch.STATUS_ACTIVE
        )

        # Обновляем записи в очереди
        player1_entry['match_id'] = match.id
        player2_entry['match_id'] = match.id

        # Удаляем из очереди
        cls.remove_player(player1_entry['player'])
        cls.remove_player(player2_entry['player'])

        # Сохраняем в активных матчах
        cls._active_matches[match.id] = match

        return match

    @classmethod
    def get_player_position(cls, player):
        """ПОЛОЖЕНИЕ ИГРОКА В ОЧЕРЕДИ"""
        for i, entry in enumerate(cls._queue):
            if entry['player'].id == player.id:
                return i + 1
        return None


# ============================================================================
# HTML ШАБЛОНЫ (как строки)
# ============================================================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Олимпиадная платформа</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #4a5568;
            margin: 0;
        }
        .header h1 a {
            text-decoration: none;
            color: inherit;
        }
        .nav {
            display: flex;
            gap: 15px;
        }
        .nav a {
            text-decoration: none;
            color: #4a5568;
            padding: 8px 16px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .nav a:hover {
            background: #667eea;
            color: white;
        }
        .nav .username {
            font-weight: bold;
            color: #667eea;
        }
        .content {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #c6f6d5;
            color: #22543d;
            border: 1px solid #9ae6b4;
        }
        .alert-error {
            background: #fed7d7;
            color: #742a2a;
            border: 1px solid #fc8181;
        }
        .alert-info {
            background: #bee3f8;
            color: #2a4365;
            border: 1px solid #90cdf4;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
        }
        .btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        .btn-danger {
            background: #e53e3e;
        }
        .btn-danger:hover {
            background: #c53030;
        }
        .btn-success {
            background: #38a169;
        }
        .btn-success:hover {
            background: #2f855a;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #4a5568;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e0;
            border-radius: 5px;
            font-size: 16px;
        }
        .form-group textarea {
            min-height: 150px;
            resize: vertical;
        }
        .tasks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .task-card {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }
        .task-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .task-card h3 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        .task-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 14px;
        }
        .difficulty {
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
        }
        .difficulty-easy {
            background: #c6f6d5;
            color: #22543d;
        }
        .difficulty-medium {
            background: #feebc8;
            color: #7b341e;
        }
        .difficulty-hard {
            background: #fed7d7;
            color: #742a2a;
        }
        .difficulty-expert {
            background: #e2e8f0;
            color: #2d3748;
        }
        .user-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .stat-card p {
            font-size: 14px;
            opacity: 0.9;
        }
        .match-card {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .match-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .match-status {
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-waiting {
            background: #feebc8;
            color: #7b341e;
        }
        .status-active {
            background: #bee3f8;
            color: #2a4365;
        }
        .status-finished {
            background: #c6f6d5;
            color: #22543d;
        }
        .status-cancelled {
            background: #e2e8f0;
            color: #4a5568;
        }
        .players {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin: 20px 0;
        }
        .player {
            text-align: center;
        }
        .player-name {
            font-weight: bold;
            font-size: 18px;
        }
        .vs {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }
        .footer a {
            color: white;
            text-decoration: none;
        }
        .login-form {
            max-width: 400px;
            margin: 0 auto;
        }
        .pvp-arena {
            background: #f7fafc;
            border-radius: 10px;
            padding: 30px;
            margin-top: 20px;
        }
        .timer {
            font-size: 48px;
            text-align: center;
            color: #e53e3e;
            font-weight: bold;
            margin: 20px 0;
        }
        .answer-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .leaderboard {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .leaderboard th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }
        .leaderboard td {
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
        }
        .leaderboard tr:hover {
            background: #f7fafc;
        }
        .rank-1 { color: gold; font-weight: bold; }
        .rank-2 { color: silver; font-weight: bold; }
        .rank-3 { color: #cd7f32; font-weight: bold; }
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                text-align: center;
                gap: 15px;
            }
            .nav {
                flex-wrap: wrap;
                justify-content: center;
            }
            .tasks-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><a href="/">🏆 Олимпиадная платформа</a></h1>
            <div class="nav">
                {% if user.is_authenticated %}
                    <a href="/">Главная</a>
                    <a href="/tasks/">Задачи</a>
                    <a href="/pvp/">PvP</a>
                    <a href="/profile/">Профиль</a>
                    <a href="/leaderboard/">Топ игроков</a>
                    <span class="username">{{ user.username }}</span>
                    <a href="/logout/" class="btn btn-danger">Выйти</a>
                {% else %}
                    <a href="/">Главная</a>
                    <a href="/login/">Войти</a>
                    <a href="/register/">Регистрация</a>
                {% endif %}
            </div>
        </div>

        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}

        <div class="content">
            {% block content %}
            {% endblock %}
        </div>

        <div class="footer">
            <p>© 2024 Олимпиадная платформа. Все права защищены.</p>
            <p>Разработано с ❤️ для подготовки к олимпиадам</p>
        </div>
    </div>

    <script>
        // Автоматическое скрытие сообщений через 5 секунд
        setTimeout(function() {
            var alerts = document.querySelectorAll('.alert');
            alerts.forEach(function(alert) {
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.style.display = 'none';
                }, 500);
            });
        }, 5000);

        // Таймер для PvP матчей
        function startTimer(duration, display) {
            var timer = duration, minutes, seconds;
            var interval = setInterval(function () {
                minutes = parseInt(timer / 60, 10);
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                display.textContent = minutes + ":" + seconds;

                if (--timer < 0) {
                    clearInterval(interval);
                    display.textContent = "Время вышло!";
                    // Можно добавить автоматическую отправку ответа
                }
            }, 1000);
        }

        // Если на странице есть таймер, запускаем его
        var timerDisplay = document.getElementById('timer');
        if (timerDisplay) {
            var timeLeft = parseInt(timerDisplay.dataset.time || 300);
            startTimer(timeLeft, timerDisplay);
        }
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
<div class="login-form">
    <h2>Вход в систему</h2>

    {% if error %}
        <div class="alert alert-error">
            {{ error }}
        </div>
    {% endif %}

    <form method="POST" action="/login/">
        {% csrf_token %}
        <div class="form-group">
            <label for="username">Имя пользователя:</label>
            <input type="text" id="username" name="username" required>
        </div>

        <div class="form-group">
            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
        </div>

        <button type="submit" class="btn">Войти</button>
    </form>

    <p style="margin-top: 20px;">
        Нет аккаунта? <a href="/register/">Зарегистрируйтесь</a>
    </p>
</div>
{% endblock %}
"""

REGISTER_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
<div class="login-form">
    <h2>Регистрация</h2>

    {% if error %}
        <div class="alert alert-error">
            {{ error }}
        </div>
    {% endif %}

    <form method="POST" action="/register/">
        {% csrf_token %}
        <div class="form-group">
            <label for="username">Имя пользователя:</label>
            <input type="text" id="username" name="username" required 
                   minlength="3" maxlength="150">
        </div>

        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>

        <div class="form-group">
            <label for="password1">Пароль:</label>
            <input type="password" id="password1" name="password1" required 
                   minlength="6">
        </div>

        <div class="form-group">
            <label for="password2">Подтвердите пароль:</label>
            <input type="password" id="password2" name="password2" required>
        </div>

        <button type="submit" class="btn btn-success">Зарегистрироваться</button>
    </form>

    <p style="margin-top: 20px;">
        Уже есть аккаунт? <a href="/login/">Войдите</a>
    </p>
</div>
{% endblock %}
"""

HOME_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <h1>Добро пожаловать на Олимпиадную платформу! 🏆</h1>

    <p style="margin: 20px 0; font-size: 18px;">
        Здесь вы можете решать олимпиадные задачи, соревноваться с другими 
        участниками и повышать свой рейтинг.
    </p>

    {% if user.is_authenticated %}
        <div class="user-stats">
            <div class="stat-card">
                <h3>{{ user.elo_rating }}</h3>
                <p>Рейтинг Elo</p>
            </div>
            <div class="stat-card">
                <h3>{{ user.total_solved }}</h3>
                <p>Решено задач</p>
            </div>
            <div class="stat-card">
                <h3>{{ win_rate }}%</h3>
                <p>Процент побед</p>
            </div>
            <div class="stat-card">
                <h3>{{ user.get_rank }}</h3>
                <p>Ваш ранг</p>
            </div>
        </div>

        <div style="margin-top: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="text-align: center;">
                <h3>🚀 Быстрый старт</h3>
                <a href="/tasks/" class="btn" style="margin-top: 10px; display: block;">
                    Решать задачи
                </a>
                <a href="/pvp/find/" class="btn btn-success" style="margin-top: 10px; display: block;">
                    Найти PvP соперника
                </a>
            </div>

            <div style="text-align: center;">
                <h3>📊 Ваша статистика</h3>
                <p>Матчи: {{ user.total_matches }} ({{ user.wins }}/{{ user.losses }}/{{ user.draws }})</p>
                <p>Серия: {{ user.get_streak_emoji }} {{ user.streak }}</p>
                <p>Баллы: {{ user.total_points }}</p>
            </div>
        </div>

        {% if active_match %}
            <div class="pvp-arena" style="margin-top: 30px;">
                <h3>⚔️ Активный PvP матч</h3>
                <div class="match-card">
                    <div class="match-header">
                        <span class="match-status status-active">Идет матч</span>
                        <span>Код: {{ active_match.match_code }}</span>
                    </div>

                    <div class="players">
                        <div class="player">
                            <div class="player-name">{{ active_match.player1.username }}</div>
                            <div>{{ active_match.player1_rating_before }}</div>
                        </div>
                        <div class="vs">VS</div>
                        <div class="player">
                            <div class="player-name">
                                {% if active_match.player2 %}
                                    {{ active_match.player2.username }}
                                {% else %}
                                    Ожидание...
                                {% endif %}
                            </div>
                            <div>
                                {% if active_match.player2 %}
                                    {{ active_match.player2_rating_before }}
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <p><strong>Задача:</strong> {{ active_match.task.title }}</p>

                    <a href="/pvp/match/{{ active_match.id }}/" class="btn">
                        Продолжить матч
                    </a>
                </div>
            </div>
        {% endif %}

    {% else %}
        <div style="text-align: center; margin-top: 40px;">
            <h2>Начните свой путь к победам!</h2>
            <p style="margin: 20px 0;">
                Присоединяйтесь к сообществу олимпиадников и улучшайте свои навыки.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px;">
                <a href="/register/" class="btn btn-success" style="padding: 15px 30px;">
                    🚀 Начать бесплатно
                </a>
                <a href="/login/" class="btn" style="padding: 15px 30px;">
                    📝 Уже есть аккаунт
                </a>
            </div>
        </div>

        <div style="margin-top: 50px; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="background: #f7fafc; padding: 20px; border-radius: 8px;">
                <h3>🎯 Решайте задачи</h3>
                <p>База олимпиадных задач с автоматической проверкой</p>
            </div>
            <div style="background: #f7fafc; padding: 20px; border-radius: 8px;">
                <h3>⚔️ Соревнуйтесь</h3>
                <p>PvP матчи с игроками вашего уровня</p>
            </div>
            <div style="background: #f7fafc; padding: 20px; border-radius: 8px;">
                <h3>📈 Растите</h3>
                <p>Система рейтинга Elo и подробная статистика</p>
            </div>
        </div>
    {% endif %}
{% endblock %}
"""

TASKS_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <h2>📚 Каталог задач</h2>

    <div style="margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap;">
        <a href="/tasks/" class="btn">Все</a>
        <a href="/tasks/?difficulty=easy" class="btn">Легкие</a>
        <a href="/tasks/?difficulty=medium" class="btn">Средние</a>
        <a href="/tasks/?difficulty=hard" class="btn">Сложные</a>
        {% for subject in subjects %}
            <a href="/tasks/?subject={{ subject.id }}" class="btn">
                {{ subject.icon }} {{ subject.name }}
            </a>
        {% endfor %}
    </div>

    <div class="tasks-grid">
        {% for task in tasks %}
            <div class="task-card">
                <h3>{{ task.title }}</h3>

                <div class="task-meta">
                    <span class="difficulty difficulty-{{ task.difficulty }}">
                        {{ task.get_difficulty_display }}
                    </span>
                    <span>🎯 {{ task.points }} баллов</span>
                </div>

                <p style="margin-bottom: 15px; color: #4a5568;">
                    {{ task.description|truncatechars:150 }}
                </p>

                <div style="font-size: 14px; color: #718096; margin-bottom: 15px;">
                    <span>✅ {{ task.success_rate }}% успеха</span>
                    <span style="float: right;">📊 {{ task.total_attempts }} попыток</span>
                </div>

                <a href="/tasks/{{ task.id }}/" class="btn" style="width: 100%; text-align: center;">
                    Решить задачу
                </a>
            </div>
        {% empty %}
            <p style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                Задачи не найдены. Попробуйте изменить фильтры.
            </p>
        {% endfor %}
    </div>
{% endblock %}
"""

TASK_DETAIL_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <h2>{{ task.title }}</h2>

    <div style="display: flex; justify-content: space-between; margin: 20px 0;">
        <span class="difficulty difficulty-{{ task.difficulty }}">
            {{ task.get_difficulty_display }}
        </span>
        <span>🎯 {{ task.points }} баллов</span>
        <span>📚 {{ task.subject }}</span>
    </div>

    <div style="background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3>Условие задачи:</h3>
        <p style="white-space: pre-line; margin-top: 10px;">{{ task.description }}</p>
    </div>

    {% if solved %}
        <div class="alert alert-success">
            <h3>✅ Задача решена!</h3>
            <p>Вы правильно решили эту задачу {{ solution.submitted_at|date:"d.m.Y H:i" }}.</p>
            <p>Ваш ответ: <strong>{{ solution.answer }}</strong></p>
            {% if task.explanation %}
                <div style="margin-top: 15px;">
                    <h4>📖 Объяснение решения:</h4>
                    <p>{{ task.explanation }}</p>
                </div>
            {% endif %}
        </div>
    {% else %}
        <form method="POST" action="/tasks/{{ task.id }}/solve/">
            {% csrf_token %}
            <div class="form-group">
                <label for="answer">Ваш ответ:</label>
                {% if task.task_type == 'text' %}
                    <textarea id="answer" name="answer" required 
                              placeholder="Введите ваш ответ..."></textarea>
                {% else %}
                    <input type="text" id="answer" name="answer" required 
                           placeholder="Введите ваш ответ...">
                {% endif %}
            </div>

            <button type="submit" class="btn">Отправить решение</button>
        </form>

        {% if attempts > 0 %}
            <div class="alert alert-info" style="margin-top: 20px;">
                Вы уже пытались решить эту задачу {{ attempts }} раз.
            </div>
        {% endif %}
    {% endif %}

    <div style="margin-top: 30px; display: flex; justify-content: space-between;">
        <a href="/tasks/" class="btn">← К списку задач</a>

        {% if not solved %}
            <a href="/pvp/create/?task={{ task.id }}" class="btn btn-success">
                ⚔️ Бросить вызов в PvP
            </a>
        {% endif %}
    </div>

    {% if similar_tasks %}
        <div style="margin-top: 40px;">
            <h3>Похожие задачи:</h3>
            <div class="tasks-grid">
                {% for similar in similar_tasks %}
                    <div class="task-card">
                        <h4>{{ similar.title }}</h4>
                        <div class="task-meta">
                            <span class="difficulty difficulty-{{ similar.difficulty }}">
                                {{ similar.get_difficulty_display }}
                            </span>
                            <span>{{ similar.points }} баллов</span>
                        </div>
                        <a href="/tasks/{{ similar.id }}/" class="btn" 
                           style="width: 100%; margin-top: 10px;">
                            Решить
                        </a>
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endif %}
{% endblock %}
"""

PVP_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <h2>⚔️ PvP Арена</h2>

    <div style="text-align: center; margin: 30px 0;">
        <p style="font-size: 18px; margin-bottom: 20px;">
            Соревнуйтесь с другими игроками в реальном времени!
        </p>
        <a href="/pvp/find/" class="btn btn-success" style="padding: 15px 30px; font-size: 18px;">
            🎮 Найти соперника
        </a>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
        <div>
            <h3>🏆 Мои матчи</h3>
            {% for match in user_matches %}
                <div class="match-card">
                    <div class="match-header">
                        <span class="match-status status-{{ match.status }}">
                            {{ match.get_status_display }}
                        </span>
                        <span>{{ match.created_at|date:"H:i" }}</span>
                    </div>

                    <div class="players">
                        <div class="player">
                            <div class="player-name">{{ match.player1.username }}</div>
                            <div>{{ match.player1_rating_before }}</div>
                            {% if match.player1_rating_change %}
                                <div style="color: {% if match.player1_rating_change > 0 %}green{% else %}red{% endif %};">
                                    {{ match.player1_rating_change|plus_sign }}
                                </div>
                            {% endif %}
                        </div>
                        <div class="vs">VS</div>
                        <div class="player">
                            <div class="player-name">
                                {% if match.player2 %}
                                    {{ match.player2.username }}
                                {% else %}
                                    ???
                                {% endif %}
                            </div>
                            <div>
                                {% if match.player2 %}
                                    {{ match.player2_rating_before }}
                                {% endif %}
                            </div>
                            {% if match.player2_rating_change %}
                                <div style="color: {% if match.player2_rating_change > 0 %}green{% else %}red{% endif %};">
                                    {{ match.player2_rating_change|plus_sign }}
                                </div>
                            {% endif %}
                        </div>
                    </div>

                    <p><strong>Задача:</strong> {{ match.task.title }}</p>

                    {% if match.status == 'active' %}
                        <a href="/pvp/match/{{ match.id }}/" class="btn">
                            Продолжить матч
                        </a>
                    {% elif match.status == 'finished' %}
                        <p>
                            <strong>Результат:</strong>
                            {% if match.player1 == user %}
                                {% if match.player1_correct %}
                                    ✅ Вы правильно ответили
                                {% else %}
                                    ❌ Ваш ответ неверен
                                {% endif %}
                            {% else %}
                                {% if match.player2_correct %}
                                    ✅ Вы правильно ответили
                                {% else %}
                                    ❌ Ваш ответ неверен
                                {% endif %}
                            {% endif %}
                        </p>
                    {% endif %}
                </div>
            {% empty %}
                <p style="text-align: center; padding: 20px;">
                    У вас еще нет матчей. Найдите первого соперника!
                </p>
            {% endfor %}
        </div>

        <div>
            <h3>📊 Статистика PvP</h3>
            <div class="user-stats">
                <div class="stat-card">
                    <h3>{{ pvp_stats.total }}</h3>
                    <p>Всего матчей</p>
                </div>
                <div class="stat-card">
                    <h3>{{ pvp_stats.wins }}</h3>
                    <p>Побед</p>
                </div>
                <div class="stat-card">
                    <h3>{{ pvp_stats.win_rate }}%</h3>
                    <p>Процент побед</p>
                </div>
                <div class="stat-card">
                    <h3>{{ pvp_stats.streak }}</h3>
                    <p>Текущая серия</p>
                </div>
            </div>

            <h3 style="margin-top: 30px;">🏅 Топ игроков в PvP</h3>
            <table class="leaderboard">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Игрок</th>
                        <th>Рейтинг</th>
                        <th>Побед</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in top_players %}
                        <tr>
                            <td class="rank-{{ forloop.counter }}">{{ forloop.counter }}</td>
                            <td>{{ player.username }}</td>
                            <td>{{ player.elo_rating }}</td>
                            <td>{{ player.wins }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
{% endblock %}
"""

PVP_MATCH_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <div class="pvp-arena">
        <h2>⚔️ PvP Матч: {{ match.match_code }}</h2>

        <div class="match-card">
            <div class="match-header">
                <span class="match-status status-active">Идет матч</span>
                <span>Время: <span id="timer" data-time="{{ time_left }}">05:00</span></span>
            </div>

            <div class="players">
                <div class="player">
                    <div class="player-name">{{ match.player1.username }}</div>
                    <div>{{ match.player1_rating_before }}</div>
                    {% if match.player1_answer %}
                        <div style="color: green;">✅ Ответ отправлен</div>
                    {% endif %}
                </div>
                <div class="vs">VS</div>
                <div class="player">
                    <div class="player-name">{{ match.player2.username }}</div>
                    <div>{{ match.player2_rating_before }}</div>
                    {% if match.player2_answer %}
                        <div style="color: green;">✅ Ответ отправлен</div>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="answer-section">
            <h3>Задача: {{ task.title }}</h3>

            <div style="background: #f7fafc; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Условие:</strong></p>
                <p>{{ task.description }}</p>
            </div>

            {% if not user_answer %}
                <form method="POST" action="/pvp/match/{{ match.id }}/answer/">
                    {% csrf_token %}
                    <div class="form-group">
                        <label for="answer">Ваш ответ:</label>
                        <textarea id="answer" name="answer" required 
                                  placeholder="Введите ваш ответ..." rows="3"></textarea>
                    </div>

                    <button type="submit" class="btn">Отправить ответ</button>
                </form>
            {% else %}
                <div class="alert alert-info">
                    <h3>📤 Ваш ответ отправлен</h3>
                    <p>Вы ответили: <strong>{{ user_answer }}</strong></p>

                    {% if opponent_answer %}
                        <div style="margin-top: 15px;">
                            <p><strong>Ответ соперника:</strong> {{ opponent_answer }}</p>
                        </div>
                    {% else %}
                        <p>Ожидаем ответа соперника...</p>
                    {% endif %}
                </div>
            {% endif %}

            <div style="margin-top: 30px; text-align: center;">
                <p>Матч завершится автоматически, когда оба игрока отправят ответы</p>
                <a href="/pvp/" class="btn">← Назад к PvP</a>
            </div>
        </div>
    </div>
{% endblock %}
"""

PROFILE_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <h2>👤 Профиль пользователя: {{ profile_user.username }}</h2>

    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 30px; margin-top: 20px;">
        <div>
            <div style="background: #f7fafc; padding: 20px; border-radius: 8px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 10px;">🏆</div>
                <h3>{{ profile_user.get_rank }}</h3>
                <p style="font-size: 24px; font-weight: bold; color: #667eea;">
                    {{ profile_user.elo_rating }} ELO
                </p>
                <p>Зарегистрирован: {{ profile_user.date_joined|date:"d.m.Y" }}</p>
            </div>

            <div style="margin-top: 20px;">
                <h3>📊 Статистика</h3>
                <p>Всего матчей: {{ profile_user.total_matches }}</p>
                <p>Побед/Поражений/Ничьих: {{ profile_user.wins }}/{{ profile_user.losses }}/{{ profile_user.draws }}</p>
                <p>Процент побед: {{ win_rate }}%</p>
                <p>Серия: {{ profile_user.get_streak_emoji }} {{ profile_user.streak }}</p>
                <p>Решено задач: {{ profile_user.total_solved }}</p>
                <p>Всего баллов: {{ profile_user.total_points }}</p>
            </div>
        </div>

        <div>
            <h3>📈 Последняя активность</h3>

            <div style="margin-top: 20px;">
                <h4>🎯 Последние решенные задачи</h4>
                {% if recent_solutions %}
                    {% for solution in recent_solutions %}
                        <div style="background: #f7fafc; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>{{ solution.task.title }}</span>
                                <span>{{ solution.submitted_at|date:"H:i" }}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #718096;">
                                <span>{{ solution.task.subject.icon }} {{ solution.task.subject.name }}</span>
                                <span>{{ solution.task.points }} баллов</span>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>Пока нет решенных задач</p>
                {% endif %}
            </div>

            <div style="margin-top: 30px;">
                <h4>⚔️ История PvP матчей</h4>
                {% if recent_matches %}
                    {% for match in recent_matches %}
                        <div style="background: #f7fafc; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>
                                    {% if match.player1 == profile_user %}
                                        vs {{ match.player2.username }}
                                    {% else %}
                                        vs {{ match.player1.username }}
                                    {% endif %}
                                </span>
                                <span class="match-status status-{{ match.status }}">
                                    {{ match.get_status_display }}
                                </span>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #718096;">
                                <span>{{ match.task.title }}</span>
                                <span style="color: {% if match.player1 == profile_user %}{% if match.player1_rating_change > 0 %}green{% else %}red{% endif %}{% else %}{% if match.player2_rating_change > 0 %}green{% else %}red{% endif %}{% endif %};">
                                    {% if match.player1 == profile_user %}
                                        {{ match.player1_rating_change|plus_sign }}
                                    {% else %}
                                        {{ match.player2_rating_change|plus_sign }}
                                    {% endif %}
                                </span>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>Пока нет PvP матчей</p>
                {% endif %}
            </div>
        </div>
    </div>
{% endblock %}
"""

LEADERBOARD_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
    <h2>🏆 Топ игроков</h2>

    <div style="margin: 20px 0; display: flex; gap: 10px;">
        <a href="/leaderboard/?type=elo" class="btn">По рейтингу</a>
        <a href="/leaderboard/?type=wins" class="btn">По победам</a>
        <a href="/leaderboard/?type=solved" class="btn">По решенным задачам</a>
        <a href="/leaderboard/?type=streak" class="btn">По серии побед</a>
    </div>

    <table class="leaderboard">
        <thead>
            <tr>
                <th>#</th>
                <th>Игрок</th>
                <th>Рейтинг</th>
                <th>Победы</th>
                <th>Решено</th>
                <th>Баллы</th>
                <th>Серия</th>
                <th>Ранг</th>
            </tr>
        </thead>
        <tbody>
            {% for player in players %}
                <tr>
                    <td class="rank-{{ forloop.counter }}">
                        {{ forloop.counter }}
                    </td>
                    <td>
                        <a href="/profile/{{ player.username }}/" style="color: inherit; text-decoration: none;">
                            {{ player.username }}
                        </a>
                    </td>
                    <td>{{ player.elo_rating }}</td>
                    <td>{{ player.wins }}</td>
                    <td>{{ player.total_solved }}</td>
                    <td>{{ player.total_points }}</td>
                    <td>{{ player.get_streak_emoji }} {{ player.streak }}</td>
                    <td>{{ player.get_rank }}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if user.is_authenticated %}
        <div style="margin-top: 40px; background: #f7fafc; padding: 20px; border-radius: 8px;">
            <h3>🎯 Ваша позиция</h3>
            <p>
                Вы на 
                <strong>{{ user_position.position }}-м месте</strong> 
                из {{ user_position.total }} игроков
            </p>
            <p>Рейтинг: <strong>{{ user.elo_rating }}</strong></p>
            <p>До следующего ранга нужно: 
                <strong>{{ user_position.points_to_next }}</strong> очков
            </p>
        </div>
    {% endif %}
{% endblock %}
"""


# ============================================================================
# ПРЕДСТАВЛЕНИЯ (VIEWS)
# ============================================================================

def render_template(template_str, context=None, request=None):
    """РЕНДЕРИНГ ШАБЛОНА ИЗ СТРОКИ"""
    if context is None:
        context = {}

    # Добавляем пользователя и сообщения в контекст
    if request:
        context['user'] = request.user
        context['messages'] = getattr(request, '_messages', [])

    # Кастомные фильтры
    def plus_sign(value):
        if value > 0:
            return f"+{value}"
        return str(value)

    context['plus_sign'] = plus_sign

    template = Template(template_str)
    return HttpResponse(template.render(Context(context)))


def home_view(request):
    """ГЛАВНАЯ СТРАНИЦА"""
    context = {
        'title': 'Главная',
    }

    if request.user.is_authenticated:
        # Статистика для авторизованных пользователей
        context['win_rate'] = request.user.calculate_win_rate()

        # Активный матч пользователя
        active_match = PvPMatch.objects.filter(
            models.Q(player1=request.user) | models.Q(player2=request.user),
            status=PvPMatch.STATUS_ACTIVE
        ).first()

        if active_match:
            context['active_match'] = active_match

    return render_template(HOME_TEMPLATE, context, request)


def login_view(request):
    """ВХОД В СИСТЕМУ"""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = {
                'title': 'Вход',
                'error': 'Неверное имя пользователя или пароль'
            }
            return render_template(LOGIN_TEMPLATE, context, request)

    return render_template(LOGIN_TEMPLATE, {'title': 'Вход'}, request)


def register_view(request):
    """РЕГИСТРАЦИЯ"""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Проверки
        errors = []

        if len(username) < 3:
            errors.append('Имя пользователя должно быть не короче 3 символов')

        if User.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует')

        if User.objects.filter(email=email).exists():
            errors.append('Пользователь с таким email уже существует')

        if password1 != password2:
            errors.append('Пароли не совпадают')

        if len(password1) < 6:
            errors.append('Пароль должен быть не короче 6 символов')

        if errors:
            context = {
                'title': 'Регистрация',
                'error': '; '.join(errors)
            }
            return render_template(REGISTER_TEMPLATE, context, request)

        # Создаем пользователя
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            # Автоматический вход после регистрации
            login(request, user)
            return redirect('/')

        except Exception as e:
            context = {
                'title': 'Регистрация',
                'error': f'Ошибка при регистрации: {str(e)}'
            }
            return render_template(REGISTER_TEMPLATE, context, request)

    return render_template(REGISTER_TEMPLATE, {'title': 'Регистрация'}, request)


def logout_view(request):
    """ВЫХОД ИЗ СИСТЕМЫ"""
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')


@login_required
def tasks_view(request):
    """СПИСОК ЗАДАЧ"""
    tasks = Task.objects.filter(is_public=True)

    # Фильтрация
    difficulty = request.GET.get('difficulty')
    if difficulty in ['easy', 'medium', 'hard', 'expert']:
        tasks = tasks.filter(difficulty=difficulty)

    subject_id = request.GET.get('subject')
    if subject_id:
        tasks = tasks.filter(subject_id=subject_id)

    # Все предметы для фильтров
    subjects = Subject.objects.all()

    context = {
        'title': 'Задачи',
        'tasks': tasks,
        'subjects': subjects,
    }

    return render_template(TASKS_TEMPLATE, context, request)


@login_required
def task_detail_view(request, task_id):
    """ДЕТАЛИ ЗАДАЧИ"""
    task = get_object_or_404(Task, id=task_id, is_public=True)

    # Проверяем, решил ли пользователь задачу
    solution = Solution.objects.filter(user=request.user, task=task).first()
    attempts = Solution.objects.filter(user=request.user, task=task).count()

    # Похожие задачи
    similar_tasks = task.get_similar_tasks()

    context = {
        'title': task.title,
        'task': task,
        'solved': solution and solution.is_correct,
        'solution': solution,
        'attempts': attempts,
        'similar_tasks': similar_tasks,
    }

    return render_template(TASK_DETAIL_TEMPLATE, context, request)


@login_required
def solve_task_view(request, task_id):
    """РЕШЕНИЕ ЗАДАЧИ"""
    if request.method != 'POST':
        return redirect(f'/tasks/{task_id}/')

    task = get_object_or_404(Task, id=task_id, is_public=True)
    answer = request.POST.get('answer', '').strip()

    if not answer:
        return redirect(f'/tasks/{task_id}/')

    # Проверяем ответ
    is_correct, message = task.check_answer(answer)

    # Сохраняем решение
    solution, created = Solution.objects.get_or_create(
        user=request.user,
        task=task,
        defaults={
            'answer': answer,
            'is_correct': is_correct,
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    )

    if not created:
        solution.answer = answer
        solution.is_correct = is_correct
        solution.submitted_at = timezone.now()
        solution.save()

    # Обновляем статистику пользователя, если решил
    if is_correct and created:
        request.user.update_stats_after_match('win', task.points)

    return redirect(f'/tasks/{task_id}/')


@login_required
def pvp_view(request):
    """ГЛАВНАЯ СТРАНИЦА PvP"""
    # Матчи пользователя
    user_matches = PvPMatch.objects.filter(
        models.Q(player1=request.user) | models.Q(player2=request.user)
    ).order_by('-created_at')[:10]

    # Статистика PvP
    pvp_stats = {
        'total': request.user.total_matches,
        'wins': request.user.wins,
        'win_rate': request.user.calculate_win_rate(),
        'streak': request.user.streak,
    }

    # Топ игроков
    top_players = User.objects.order_by('-elo_rating')[:10]

    context = {
        'title': 'PvP Арена',
        'user_matches': user_matches,
        'pvp_stats': pvp_stats,
        'top_players': top_players,
    }

    return render_template(PVP_TEMPLATE, context, request)


@login_required
def find_opponent_view(request):
    """ПОИСК СОПЕРНИКА"""
    # Проверяем, не в активном матче ли уже пользователь
    active_match = PvPMatch.objects.filter(
        (models.Q(player1=request.user) | models.Q(player2=request.user)) &
        models.Q(status=PvPMatch.STATUS_ACTIVE)
    ).first()

    if active_match:
        return redirect(f'/pvp/match/{active_match.id}/')

    # Добавляем в очередь matchmaking
    queue_entry = MatchmakingQueue.add_player(request.user, request.user.elo_rating)

    # Проверяем, нашли ли соперника
    if queue_entry.get('match_id'):
        match = PvPMatch.objects.get(id=queue_entry['match_id'])
        return redirect(f'/pvp/match/{match.id}/')
    else:
        # Показываем страницу ожидания
        position = MatchmakingQueue.get_player_position(request.user)

        # В реальном проекте здесь был бы WebSocket для обновления статуса
        # Здесь просто редирект на PvP страницу с сообщением
        return redirect('/pvp/?message=Ищем соперника...')


@login_required
def pvp_match_view(request, match_id):
    """СТРАНИЦА PvP МАТЧА"""
    match = get_object_or_404(PvPMatch, id=match_id)

    # Проверяем, что пользователь участник матча
    if request.user not in [match.player1, match.player2]:
        return redirect('/pvp/')

    # Определяем ответы пользователя и соперника
    if request.user == match.player1:
        user_answer = match.player1_answer
        opponent_answer = match.player2_answer
    else:
        user_answer = match.player2_answer
        opponent_answer = match.player1_answer

    # Время до конца матча (5 минут)
    if match.started_at:
        time_passed = (timezone.now() - match.started_at).seconds
        time_left = max(0, 300 - time_passed)  # 5 минут = 300 секунд
    else:
        time_left = 300

    context = {
        'title': f'Матч {match.match_code}',
        'match': match,
        'task': match.task,
        'user_answer': user_answer,
        'opponent_answer': opponent_answer,
        'time_left': time_left,
    }

    return render_template(PVP_MATCH_TEMPLATE, context, request)


@login_required
def submit_pvp_answer_view(request, match_id):
    """ОТПРАВКА ОТВЕТА В PvP МАТЧЕ"""
    if request.method != 'POST':
        return redirect(f'/pvp/match/{match_id}/')

    match = get_object_or_404(PvPMatch, id=match_id)

    # Проверяем, что пользователь участник и матч активен
    if request.user not in [match.player1, match.player2] or match.status != PvPMatch.STATUS_ACTIVE:
        return redirect('/pvp/')

    answer = request.POST.get('answer', '').strip()

    if not answer:
        return redirect(f'/pvp/match/{match_id}/')

    # Определяем номер игрока
    player_num = 1 if request.user == match.player1 else 2

    # Отправляем ответ
    match.submit_answer(player_num, answer)

    return redirect(f'/pvp/match/{match_id}/')


@login_required
def profile_view(request, username=None):
    """ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ"""
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    # Статистика
    win_rate = profile_user.calculate_win_rate()

    # Последние решения
    recent_solutions = Solution.objects.filter(
        user=profile_user,
        is_correct=True
    ).order_by('-submitted_at')[:10]

    # Последние матчи
    recent_matches = PvPMatch.objects.filter(
        models.Q(player1=profile_user) | models.Q(player2=profile_user)
    ).order_by('-created_at')[:10]

    context = {
        'title': f'Профиль {profile_user.username}',
        'profile_user': profile_user,
        'win_rate': win_rate,
        'recent_solutions': recent_solutions,
        'recent_matches': recent_matches,
    }

    return render_template(PROFILE_TEMPLATE, context, request)


def leaderboard_view(request):
    """ТАБЛИЦА ЛИДЕРОВ"""
    sort_type = request.GET.get('type', 'elo')

    if sort_type == 'wins':
        players = User.objects.order_by('-wins', '-elo_rating')
    elif sort_type == 'solved':
        players = User.objects.order_by('-total_solved', '-elo_rating')
    elif sort_type == 'streak':
        players = User.objects.order_by('-streak', '-elo_rating')
    else:  # По умолчанию по рейтингу
        players = User.objects.order_by('-elo_rating', '-total_solved')

    # Позиция текущего пользователя
    user_position = None
    if request.user.is_authenticated:
        # Простой расчет позиции (в реальном проекте нужно оптимизировать)
        all_users = list(User.objects.order_by('-elo_rating'))
        for i, user in enumerate(all_users, 1):
            if user == request.user:
                points_to_next = 0
                if i > 1:
                    points_to_next = all_users[i - 2].elo_rating - user.elo_rating + 1

                user_position = {
                    'position': i,
                    'total': len(all_users),
                    'points_to_next': points_to_next,
                }
                break

    context = {
        'title': 'Таблица лидеров',
        'players': players[:100],  # Только топ 100
        'user_position': user_position,
    }

    return render_template(LEADERBOARD_TEMPLATE, context, request)


def create_sample_data():
    """СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ"""
    if User.objects.filter(username='admin').exists():
        return  # Данные уже созданы

    print("Создание тестовых данных...")

    # Создаем суперпользователя
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@olympiad.ru',
        password='admin123'
    )

    # Создаем обычных пользователей
    users = []
    for i in range(1, 11):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password=f'user{i}123'
        )
        # Устанавливаем разный рейтинг
        user.elo_rating = 1000 + (i * 50)
        user.total_solved = i * 3
        user.total_points = i * 30
        user.wins = i * 2
        user.losses = i
        user.total_matches = user.wins + user.losses + user.draws
        user.save()
        users.append(user)

    # Создаем предметы
    subjects = [
        Subject.objects.create(name='Математика', icon='🧮', description='Задачи по математике'),
        Subject.objects.create(name='Информатика', icon='💻', description='Программирование и алгоритмы'),
        Subject.objects.create(name='Физика', icon='⚛️', description='Физические задачи'),
        Subject.objects.create(name='Логика', icon='🧩', description='Логические задачи'),
    ]

    # Создаем задачи
    tasks_data = [
        {
            'title': 'Сумма чисел',
            'description': 'Найдите сумму всех натуральных чисел от 1 до 100.',
            'subject': subjects[0],  # Математика
            'difficulty': Task.DIFFICULTY_EASY,
            'points': 10,
            'correct_answer': '5050',
        },
        {
            'title': 'Числа Фибоначчи',
            'description': 'Найдите 10-е число Фибоначчи (F(1)=1, F(2)=1).',
            'subject': subjects[0],
            'difficulty': Task.DIFFICULTY_MEDIUM,
            'points': 20,
            'correct_answer': '55',
        },
        {
            'title': 'Алгоритм сортировки',
            'description': 'Какой алгоритм сортировки имеет сложность O(n log n) в среднем случае?',
            'subject': subjects[1],  # Информатика
            'difficulty': Task.DIFFICULTY_MEDIUM,
            'points': 15,
            'correct_answer': 'быстрая сортировка',
        },
        {
            'title': 'Законы Ньютона',
            'description': 'Сформулируйте первый закон Ньютона.',
            'subject': subjects[2],  # Физика
            'difficulty': Task.DIFFICULTY_EASY,
            'points': 10,
            'correct_answer': 'тело сохраняет состояние покоя или равномерного прямолинейного движения пока на него не действуют силы',
        },
        {
            'title': 'Логическая задача',
            'description': 'Что идет, не двигаясь с места?',
            'subject': subjects[3],  # Логика
            'difficulty': Task.DIFFICULTY_HARD,
            'points': 30,
            'correct_answer': 'время',
        },
    ]

    tasks = []
    for task_data in tasks_data:
        task = Task.objects.create(
            title=task_data['title'],
            description=task_data['description'],
            subject=task_data['subject'],
            difficulty=task_data['difficulty'],
            points=task_data['points'],
            correct_answer=task_data['correct_answer'],
            author=admin,
            is_public=True
        )
        tasks.append(task)

    # Создаем несколько решений
    for i, user in enumerate(users[:5]):
        for j, task in enumerate(tasks[:3]):
            is_correct = (i + j) % 2 == 0  # Чередуем правильные/неправильные
            Solution.objects.create(
                user=user,
                task=task,
                answer=str(i * j) if not is_correct else task.correct_answer,
                is_correct=is_correct,
                time_spent=random.randint(30, 300),
            )

    # Создаем несколько PvP матчей
    for i in range(5):
        player1 = users[i]
        player2 = users[i + 1] if i < 4 else users[0]
        task = random.choice(tasks)

        match = PvPMatch.objects.create(
            player1=player1,
            player2=player2,
            task=task,
            status=PvPMatch.STATUS_FINISHED,
            started_at=timezone.now() - timezone.timedelta(minutes=10),
            finished_at=timezone.now() - timezone.timedelta(minutes=5),
            player1_rating_before=player1.elo_rating,
            player2_rating_before=player2.elo_rating,
        )

        # Симулируем результаты
        match.player1_correct = random.choice([True, False])
        match.player2_correct = random.choice([True, False])
        match.calculate_results()
        match.update_player_stats()
        match.save()

    print("Тестовые данные созданы!")
    print(f"Создано: {User.objects.count()} пользователей, {Task.objects.count()} задач")
    print("Админ: логин - admin, пароль - admin123")
    print("Пользователи: user1-user10, пароли: userX123")


# ============================================================================
# URL МАРШРУТЫ
# ============================================================================

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('tasks/', tasks_view, name='tasks'),
    path('tasks/<int:task_id>/', task_detail_view, name='task_detail'),
    path('tasks/<int:task_id>/solve/', solve_task_view, name='solve_task'),

    path('pvp/', pvp_view, name='pvp'),
    path('pvp/find/', find_opponent_view, name='find_opponent'),
    path('pvp/match/<int:match_id>/', pvp_match_view, name='pvp_match'),
    path('pvp/match/<int:match_id>/answer/', submit_pvp_answer_view, name='submit_pvp_answer'),

    path('profile/', profile_view, name='my_profile'),
    path('profile/<str:username>/', profile_view, name='profile'),

    path('leaderboard/', leaderboard_view, name='leaderboard'),
]

# ============================================================================
# ОСНОВНОЙ БЛОК ЗАПУСКА
# ============================================================================

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    # Если переданы аргументы командной строки (например, migrate, runserver)
    if len(sys.argv) > 1:
        execute_from_command_line(sys.argv)
    else:
        # По умолчанию запускаем сервер
        print("=" * 60)
        print("🏆 ОЛИМПИАДНАЯ ПЛАТФОРМА НА DJANGO")
        print("=" * 60)
        print()
        print("Команды:")
        print("  python olympiad_platform.py migrate     # Создать БД")
        print("  python olympiad_platform.py createsuperuser  # Создать админа")
        print("  python olympiad_platform.py runserver   # Запустить сервер")
        print("  python olympiad_platform.py shell       # Открыть консоль")
        print()
        print("Для запуска тестовых данных выполните:")
        print("  python olympiad_platform.py migrate")
        print("  python olympiad_platform.py runserver")
        print("  Затем откройте http://127.0.0.1:8000/ в браузере")
        print("=" * 60)

        # Создаем тестовые данные если база пустая
        try:
            if not User.objects.exists():
                print("\n🔄 Создание тестовых данных...")
                create_sample_data()
                print("✅ Готово! Теперь запустите сервер:")
                print("   python olympiad_platform.py runserver")
        except:
            print("⚠️  Не удалось создать тестовые данные. Сначала выполните миграции.")