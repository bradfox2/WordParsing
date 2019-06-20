import docker
import dotenv
import os
import socket
import requests

hostname = socket.gethostname()
#start a unoconv service if a url to the service wasnt specified
def start_unoconv(container_name, service_port):
    '''a unoconv container will be started with container_name'''

    #see if another container is running, if not make a new one 
    client = docker.from_env()
    nms = [container.name for container in client.containers.list()]
    if container_name not in nms:
        unoconv = client.containers.run("bradfox2/unoconv:latest",
                                    detach=True,
                                    remove=True,
                                    ports={'3000/tcp': service_port},
                                    name=container_name)
        return f'http://{hostname}:{service_port}', unoconv
    else:
        #return existing container
        unoconv = list(filter(lambda x: x.name==container_name, client.containers.list()))[0]
        unurl = f'http://{hostname}:{service_port}'
        os.putenv('UNOCONV_URL', unurl)
        return unurl, unoconv

if __name__ == "__main__":
    a = start_unoconv('unoconv_test', 3001)
    
