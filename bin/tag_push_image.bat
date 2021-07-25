@echo off
set repo_name=lojames/test:latest
docker tag flask-app %repo_name%
docker images
docker push %repo_name%
pause
