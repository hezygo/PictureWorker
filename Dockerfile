FROM python:3.7.10-slim-buster

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
WORKDIR /fast_app
ENV JS_DRIVER='/fast_app/phj/bin/phantomjs'
COPY . .
EXPOSE 80
CMD ["uvicorn", "fRun:fast_app", "--host", "0.0.0.0", "--port", "80"]
#  -v ./tmp/pic:/fast_app/tmp/pic
