# Интернет-магазин

## Как установить
Для работы сервиса требуются:
- Python версии не ниже 3.10.
- установленное ПО для контейнеризации - [Docker](https://docs.docker.com/engine/install/).
- Инструмент [poetry](https://python-poetry.org/) для управления зависимостями и сборкой пакетов в Python.

Настройка переменных окружения
1. Скопируйте файл .env.dist в .env
2. Заполните .env файл. Пример:
```yaml
DATABASE_URL = URL
REDIS_URL = URL
SECRET_KEY = "django-insecure-=e-i4d_qq&ra7un4)u8bdr#gf08q)gc_*yyy4@7--kt(0(p#!("
DEBUG = True
ALLOWED_HOSTS = www.allowed.com www.host.com
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "example@gmail.com"
EMAIL_HOST_PASSWORD = "example password"
```

Установка и активация виртуального окружения
```shell
poetry install  ; установка пакетов
poetry shell  ; активация виртуального окружения
pre-commit install  ; установка pre-commit для проверки форматирования кода, см. .pre-commit-config.yaml
```
Запуск менеджера задач Celery, планировщика задач Celery-beat и плагина Flower для мониторинга задач в режиме реального времени
```shell
celery -A config worker --loglevel=INFO

# ОС Windows
celery -A config worker --loglevel=INFO --pool=solo

celery -A config beat -l INFO

celery -A config flower --loglevel=INFO
```

## Проверка форматирования кода
Проверка кода выполняется из корневой папки репозитория.
* Анализатор кода flake8
```shell
flake8 market
```
* Линтер pylint
```shell
pylint --rcfile=.pylintrc market/*
```
* Линтер black
```shell
black market
```

## Как запустить web-сервер
Запуск сервера производится в активированном локальном окружение из папки `market/`
```shell
python manage.py runserver 0.0.0.0:8000
```