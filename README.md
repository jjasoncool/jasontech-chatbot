# django-chatbot-api

## Setup

```
docker-compose up -d
```

## connect db
- settings.py using mysql
```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOST', 'localhost'),           # 連接到 docker-compose 中的服務名
        'PORT': os.getenv('DB_PORT', '5432'),                # PostgreSQL 預設端口
        'NAME': os.getenv('DB_DATABASE', 'django_db'),       # 從環境變量中讀取，或設定預設值
        'USER': os.getenv('DB_USER', 'your_username'),
        'PASSWORD': os.getenv('DB_PASS', 'your_password'),
    }
}

```
