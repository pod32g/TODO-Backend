FROM python:3.9.1

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN python manage.py test

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]