FROM python:3.11-slim-bullseye
COPY . /opt/gmail-osint
WORKDIR /opt/gmail-osint
RUN python3 setup.py install
