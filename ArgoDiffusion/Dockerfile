FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get upgrade -y 
RUN apt-get install -y wget maven python tcsh expect jq  bc  python-pip python-dev build-essential libgeos-dev nmap git screen parallel
RUN yum install -y python tcsh

WORKDIR /root
RUN ls
ADD scripts scripts
ADD data_argo data_argo
WORKDIR scripts
RUN chmod +x generation_argo_big_data.csh
# RUN ./generation_argo_big_data.csh configuration.json

# ENTRYPOINT ./generation_argo_big_data.csh configuration.json
#Build: docker build -t argo_diffusion .
#Run: docker run -i -t  argo_diffusion /bin/bash