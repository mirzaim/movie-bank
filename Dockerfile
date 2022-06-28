FROM        alpine:3.15.0

RUN         apk --no-cache add python3 py3-pip

COPY        ./requirements.txt /app/requirements.txt
WORKDIR     /app
RUN         pip3 install -r requirements.txt

COPY        /app/ /app/

ENTRYPOINT  ["python3"]
CMD         ["app.py"]