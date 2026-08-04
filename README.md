
# DRF Homework

Проект для управления курсами, уроками и платежами с использованием Django REST Framework, Celery и PostgreSQL.

## Запуск проекта через Docker

###  Скопируйте переменные окружения

```bash

cp .env.example .env

bash
docker-compose up -d --build
```
## Примените миграции
docker-compose exec web python manage.py migrate
```


```
### Создайте суперпользователя
bash
docker-compose exec web python manage.py createsuperuser

### Соберите статику (опционально)
docker-compose exec web python manage.py collectstatic
Проверка работы
Админка: http://localhost:8000/admin

Swagger: http://localhost:8000/swagger/

Redoc: http://localhost:8000/redoc/

API: http://localhost:8000/api/

### Остановка проекта
bash
docker-compose down
Структура сервисов
web — Django приложение

db — PostgreSQL

redis — брокер для Celery

celery — воркер для фоновых задач

celery-beat — планировщик периодических задач

### Переменные окружения
Все настройки хранятся в файле .env. Пример доступен в .env.example.

Основные переменные:

DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

SECRET_KEY, DEBUG, ALLOWED_HOSTS

REDIS_HOST, REDIS_PORT

EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

text

---

##  Проверяем и коммитим

```bash
cat README.md
git add README.md
git commit -m
``` 
