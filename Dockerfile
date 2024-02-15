FROM python:3.12

# Set environment variables
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

# install dependencies
RUN apt-get update
RUN apt-get install -y gcc musl-dev libpq-dev libffi-dev zlib1g-dev g++ libev-dev git build-essential \
    libev4 ca-certificates mailcap debian-keyring debian-archive-keyring apt-transport-https

WORKDIR /usr/src/app/

RUN pip3 install -U pip

RUN groupadd -g 1000 app && \
    useradd -r -u 1000 -g app app

RUN mkdir "/home/app"
RUN	chown -R app:app /home/app

COPY ./requirements.txt /usr/src/requirements.txt
RUN pip3 install -r /usr/src/requirements.txt

COPY . /usr/src/
RUN	chown -R app:app /usr/src/
RUN chmod +x /usr/src/app/entrypoint.sh

USER app

EXPOSE 8080
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD [ "gunicorn", "main:app", "--workers", "2", "--worker-class", \
		"uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080" ]
