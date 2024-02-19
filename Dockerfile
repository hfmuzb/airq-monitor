FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /code/app/

RUN pip install -U pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /code/

EXPOSE 8080

ENTRYPOINT ["/code/app/entrypoint.sh"]

CMD [ "gunicorn", "main:app", "--workers", "2", "--worker-class", \
		"uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080" ]
