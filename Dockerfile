FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /code/app/

RUN pip install -U pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /code/


RUN groupadd -g 1000 app && \
    useradd -r -u 1000 -g app app

RUN mkdir "/home/app"
RUN	chown -R app:app /home/app


RUN	chown -R app:app /code/
RUN chmod +x /code/app/entrypoint.sh

EXPOSE 8080
USER app

ENTRYPOINT ["/code/app/entrypoint.sh"]

CMD [ "gunicorn", "main:app", "--workers", "2", "--worker-class", \
		"uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080" ]
