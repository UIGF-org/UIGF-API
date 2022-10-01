docker build -f Dockerfile -t uigf-api/1.0 .
docker run -d -itp 3052:8080 \
    --name=UIGF-API-1.0 \
    --mount type=bind,source="$(pwd)"/config,target=/code/config \
    --mount type=bind,source="$(pwd)"/dict,target=/code/dict \
    uigf-api/1.0