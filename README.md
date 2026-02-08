# Сервис управления столовой для олимпиады (MealHub)

Сервер управления столовой для олимпиады. Проект построен на Django и использует SQLite по умолчанию.

## Быстрый старт

### Подключение виртуального окружения и установка зависимостей

```bash
python -m venv venv

#Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Миграции и загрузка начальных данных аллергенов

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata allergens.json
```

### Создание суперпользователя

```bash
python manage.py createsuperuser
```

### Запуск сервера

```bash
python manage.py runserver
```


