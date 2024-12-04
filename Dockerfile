#!/bin/sh
# Build Stage
FROM python:3.12 AS builder
WORKDIR /code
ADD . /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pyinstaller -F main.py

# Runtime
FROM ubuntu:22.04 AS runtime
WORKDIR /app
COPY --from=builder /code/dist/main .
EXPOSE 8000
ENTRYPOINT ["./main"]
