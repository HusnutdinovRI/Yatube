# Проект «Yatube»

## Описание проекта.

Социальная сеть, в которой можно создавать посты, группы по интересам, а комментировать посты других пользователей, а также подписываться на других пользователей.

## Установка:


Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/HusnutdinovRI/HusnutdinovRI/Yatube.git
```

```
cd yatube
```

### *Установка на Windows:*

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/source/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### *Установка на Mac OS и Linux:*

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
## *Технологии использованые в проекте:*

- Python 3
- Django 2.2
- HTML 5
- CSS3
