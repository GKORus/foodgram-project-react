[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)


# Описание проекта Foodgram
"Foodgram" является платформой, которая объединяет людей с разнообразными интересами в кулинарии. Проект предлагает возможность пользователям делиться своим кулинарными рецептами: 
1. Публикация Рецептов: зарегистрированные пользователи могут публикуя свои собственные рецепты. 
2. Просмотр Рецептов и Профилей: неавторизированные и зарегистрированные пользователи имеют доступ к уже сформированной на сайте коллекции рецептов. 
3. Список "Избранное": пользователи могут сохранять понравившиеся рецепты в свой персональный список "Избранное". 
4. Создание сводного списка продуктов: зарегистрированные пользователи имеют возможность ознакомиться и скачать списка продуктов понравившегося рецепта в формате .txt.

[![for-github.jpg](https://i.postimg.cc/Gh48mkk5/for-github.jpg)](https://postimg.cc/0bq2tKXY)

## Запуск проекта на удаленном сервере
Для запуска проектан на удаленном сервере необходимо выполнить следующие действия:

- сохранить на удаленном сервере docker-compose.production.yml;
- сформируйте .env файл на удаленном сервере:<br>
<br>Конфигурационный файл .env<br>
POSTGRES_USER=django_user # Имя пользователя базы данных PostgreSQL<br>
POSTGRES_PASSWORD=mysecretpassword # Пароль пользователя базы данных PostgreSQL<br>
POSTGRES_DB=django # Имя базы данных PostgreSQL, которую будет использовать проект<br>
DB_HOST=db # Хост (адрес) сервера базы данных PostgreSQL<br>
DB_PORT=5432 # Порт для подключения к базе данных PostgreSQL<br>
SECRET_KEY='SECRET_KEY'	# Ваш секретный ключ Django, который используется для шифрования данных

- сформируйте файл nginx на удаленном сервере;
- запустите на удаленном сервере контейнеры скачав их Dockerhub запустив файл docker-compose.production.yml на удаленном сервере командой:
```
docker compose -f docker-compose.production.yml up
```
- соберите статику:
```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
- осуществите миграции:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
- создать администратора проекта: 
```
sudo docker-compose exec web python manage.py createsuperuser
```
## Инструкции для локального запуска
***- Клонируйте репозиторий:***
```
git clone git@github.com:GKORus/foodgram-project-react.git
```

***- Установите и активируйте виртуальное окружение:***
- для MacOS
```
python3 -m venv venv
```
- для Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
pip install -r requirements.txt
```

***- Создайте и Примените миграции:***
```
python manage.py makemigrations
python manage.py migrate
```

***- Создайте супе-пользователя (Библиотекаря):***
```
python manage.py createsuperuser
```

***- В папке с файлом manage.py выполните команду для запуска локально:***
```
python manage.py runserver
```

***- Проект на данной стадии доступен по локальным адресам dev сервера:***
```
http://127.0.0.1:8000/admin/ - Панель администратора
http://127.0.0.1:8000/api/ - API проекта

```
