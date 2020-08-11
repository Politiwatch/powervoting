FROM python:3-alpine
RUN apk add build-base
WORKDIR /powervoting
RUN pip3 install pipenv
ADD Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system
ADD src .
ENTRYPOINT ["gunicorn", "main:app"]