# Docker Image Settings
imageName=uigf-api
containerName=UIGF-API
imageVersion=1.1
internalPort=3052
ExternalPort=8080
# Docker Network Settings
assignedNetwork=dgp-network
assignedIP=172.18.0.3
# App Settings
TOKEN=H3HYiDe84tZzWqHc
DOCS_URL=/api/v1/docs
# MySQL Settings
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=uigf
DB_PASSWORD=uigf
DB_NAME=uigf_dict

docker build -f Dockerfile -t $imageName:$imageVersion .
docker run -d -itp $internalPort:$ExternalPort \
    --restart=always \
    --name="$containerName-$imageVersion" \
    --net $assignedNetwork --ip $assignedIP \
    --mount type=bind,source="$(pwd)"/dict,target=/code/dict \
    --env TOKEN=$TOKEN \
    --env DOCS_URL=$DOCS_URL \
    --env DB_HOST=$DB_HOST \
    --env DB_PORT=$DB_PORT \
    --env DB_USER=$DB_USER \
    --env DB_PASSWORD=$DB_PASSWORD \
    --env DB_NAME=$DB_NAME \
    $imageName:$imageVersion