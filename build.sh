# Image Settings
imageName=uigf-api
imageVersion=1.4

docker build --no-cache -f Dockerfile -t $imageName:$imageVersion --target runtime .