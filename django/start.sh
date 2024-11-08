# start.sh
#!/bin/bash

# 從第一行到最后一行分別表示：
# 1. 收集靜態文件
# 2. 生成數據庫遷移文件
# 3. 根據數據庫遷移文件來修改數據庫
# 4. 啟動 django 服務, 分為python manage.py runserver(dev) 與 uwsgi(prod)

python manage.py collectstatic --noinput &&
python manage.py makemigrations &&
python manage.py migrate &&

# development server
# python manage.py runserver 0.0.0.0:8000

# uwsgi
uwsgi --ini /usr/src/app/${PROJECT_NAME}/uwsgi.ini
