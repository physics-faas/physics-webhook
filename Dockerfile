FROM python:3.8-alpine

RUN mkdir /app
ADD webhook_server.py /app
WORKDIR /app
RUN pip install Flask jsonpatch
CMD [ "python", "webhook_server.py" ]
