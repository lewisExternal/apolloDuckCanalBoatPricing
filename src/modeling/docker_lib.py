import docker 
import sys
from io import BytesIO
from docker import APIClient
from os import getcwd

# import scripts 
sys.path.append('../utils/')
from utils import get_time_stamp

# docker build -t flask-tutorial:latest .
# docker run -i -t -p  5000:5000 flask-tutorial
# docker ps -a

def build_docker_image(client):
    try:
        print( get_time_stamp() + ' - INFO - build docker container')
        client.images.build(path="./",tag='flask-app',encoding=None,dockerfile="./Dockerfile")
    except Exception as e:
        
        # if legitimate error then exit  
        if 'error' in str(e).lower():
            exit(1)
        
        print (str(e)) 

def run_docker_image(client):
    print( get_time_stamp() + ' - INFO - run docker container')
    myContainer=client.api.create_container(image='flask-app', host_config=client.api.create_host_config(port_bindings={5000: 5000}))
    container  = client.containers.run('flask-app', detach=True,ports={'5000/tcp': 5000})
    #print(container.logs())

def create_and_run_docker():
    client = docker.from_env()
    build_docker_image(client)
    run_docker_image(client)


if __name__ == "__main__":
    create_and_run_docker()
