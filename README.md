# DRF Homework

## Запуск проекта

1. Скопируйте `.env.example` в `.env` и заполните переменные.
2. Выполните команду:
   ```bash
   docker-compose up -d --build
Примените миграции:

bash
docker-compose exec web python manage.py migrate
Создайте суперпользователя:

bash
docker-compose exec web python manage.py createsuperuser
Доступные эндпоинты
Админка: http://localhost:8000/admin

Swagger: http://localhost:8000/swagger/

API: http://localhost:8000/api/
```