# **Barter Exchange** — Платформа для обмена вещами

**Barter Exchange** — это Django-приложение, где пользователи могут размещать объявления и предлагать обмен вещами. 

---

## **Функциональность**

- **Регистрация и авторизация** (Login / Logout)
- **Работа с объявлениями**: создание, просмотр, редактирование, удаление
- **Поиск и фильтрация** по объявлениям
- **Просмотр только своих объявлений**
- **Обмен вещами**:
  - Создание предложений обмена
  - Принятие или отклонение предложений
  - Система статусов (ожидание, принято, отклонено)
- **Swagger-документация API** для разработчиков

---

## **Технологии**

- **Backend**: Django, Django ORM
- **База данных**: PostgreSQL
- **Frontend**: Django Templates + Bootstrap 5
- **Аутентификация**: Django built-in auth
- **Документация API**: drf-spectacular + Swagger UI

---

## **Установка проекта**

```bash
git clone https://github.com/August-Genji/barter-exchange.git
cd barter-exchange
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## **Настройка базы данных (PostgreSQL)**

 Создание базы данных и пользователя:

```sql
CREATE DATABASE barter_db;
CREATE USER barter_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE barter_db TO barter_user;
```

В `settings.py` указать:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barter_db',
        'USER': 'barter_user',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## **Запуск приложения**

```bash
python manage.py migrate
python manage.py runserver
```

---

## **Создание суперпользователя**

```bash
python manage.py createsuperuser
```

---

## **Swagger-документация**

Доступна по адресу:

[http://127.0.0.1:8000/api/schema/swagger/](http://127.0.0.1:8000/api/schema/swagger/)

---

## **Запуск тестов**

```bash
python manage.py test
```

---

## **Контакты**

**Автор:** August Genji  
[GitHub профайл](https://github.com/August-Genji)
