FROM python:3.9.7-slim

WORKDIR /tele-forwarder

COPY main.py main.py
COPY requirements.txt requirements.txt
COPY templates/ templates/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]