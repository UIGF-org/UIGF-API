imageName=uigf-api
containerName=UIGF-API
imageVersion=1.1
internalPort=3052
ExternalPort=8080

docker build -f Dockerfile -t $imageName:$imageVersion .
docker run -d -itp $internalPort:$ExternalPort \
    --restart=always \
    --name="$containerName-$imageVersion" \
    --mount type=bind,source="$(pwd)"/config,target=/code/config \
    --mount type=bind,source="$(pwd)"/dict,target=/code/dict \
    $imageName:$imageVersion