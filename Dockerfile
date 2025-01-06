#!/bin/sh
# Build Stage
FROM python:3.12 AS builder
WORKDIR /code
ADD . /code
RUN pip install "fastapi[standard]"
RUN pip install redis
RUN pip install sqlalchemy
RUN pip install pymysql
RUN pip install pyinstaller
RUN pyinstaller -F main.py

# Runtime
FROM ubuntu:22.04 AS runtime
WORKDIR /app
COPY --from=builder /code/dist/main .
EXPOSE 8000
ENTRYPOINT ["./main"]
