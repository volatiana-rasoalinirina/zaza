FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/base.txt requirements/base.txt
RUN apt-get update && apt-get install -y gettext
RUN pip install --no-cache-dir -r requirements/base.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]