import docker
import dotenv
import os

#start a unoconv service if a url to the service wasnt specified
UNOCONV_URL = os.getenv('UNOCONV_URL')
if UNOCONV_URL is None: 
    client = docker.from_env()
    nms = [container.name for container in client.containers.list()]
    if 'unoconv' not in nms:
        unoconv = client.containers.run("bradfox2/unoconv:latest",
                                    detach=True,
                                    ports={'3000/tcp':3000},
                                    name='unoconv')
    UNOCONV_URL = 'http://localhost:3000' 