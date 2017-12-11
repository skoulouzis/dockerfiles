FROM ubuntu:16.04
MAINTAINER S. Koulouzis 

RUN apt-get update -y
RUN apt-get upgrade -y 
RUN apt-get install -y openssh-client curl 

RUN  curl -L http://go.egi.eu/fedcloud.ui | /bin/bash -
RUN fetch-crl --httptimeout 3 --verbose 

WORKDIR /root

# ENTRYPOINT scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r $USER@172.17.0.1:/home/$USER/.globus/ . && fetch-crl --verbose && voms-proxy-init --voms fedcloud.egi.eu --rfc -cert .globus/usercert.pem -key .globus/userkey.pem -out /tmp/x509up_u1000 && scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/x509up_u1000 $USER@172.17.0.1:/tmp

ENTRYPOINT scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r $USER@172.17.0.1:/home/$USER/.globus/ . && rm -rf /tmp/x509up_u1000 && voms-proxy-init --voms fedcloud.egi.eu --rfc -cert .globus/usercert.pem -key .globus/userkey.pem -out /tmp/x509up_u1000 && scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/x509up_u1000 $USER@172.17.0.1:/tmp

#sudo docker build -t fed-ui .
#sudo docker run -i -t -P  -e USER=`echo $USER` fed-ui 
#sudo docker run -t -i fed-ui /bin/bash
