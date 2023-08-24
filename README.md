# Foodgram

- Проект размещен на сайте: https://tmukhor.sytes.net
- Адрес домена: 51.250.107.251
- Логин администратора: kirill
- Пароль администратора: 1

# Описание
"Foodgram" является платформой, которая объединяет людей с разнообразными интересами в кулинарии. Проект предлагает возможность пользователям делиться своим кулинарными рецептами: 
1. Публикация Рецептов: зарегистрированные пользователи могут публикуя свои собственные рецепты. 
2. Просмотр Рецептов и Профилей: неавторизированные и зарегистрированные пользователи имеют доступ к уже сформированной на сайте коллекции рецептов. 
3. Список "Избранное": пользователи могут сохранять понравившиеся рецепты в свой персональный список "Избранное". 
4. Создание сводного списка продуктов: зарегистрированные пользователи имеют возможность ознакомиться и скачать списка продуктов понравившегося рецепта в формате .txt.

# Запуск проекта на удаленном сервере
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
- запустите на удаленном сервере контейнеры скачав их Dockerhub запустив файл docker-compose.production.yml на удаленном сервере командой docker compose -f docker-compose.production.yml up
- соберите статику:
```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
- осуществите миграции:
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
- создать администратора проекта: 
sudo docker-compose exec web python manage.py createsuperuser
