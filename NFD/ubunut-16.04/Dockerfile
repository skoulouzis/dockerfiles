FROM ubuntu:16.04

RUN DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get upgrade -y 
RUN apt-get install -y software-properties-common git pkg-config wget python-sphinx python-pip 
RUN add-apt-repository ppa:named-data/ppa
RUN apt-get update -y
RUN pip install --upgrade pip
RUN pip install sphinxcontrib-doxylink sphinxcontrib-googleanalytics
RUN apt-get install -y nfd #ndn-cxx-dev g++ libpcap-dev


# WORKDIR /root
# RUN git clone https://github.com/named-data/ndn-tools.git 
# WORKDIR ndn-tools
# RUN ./waf configure
# RUN ./waf
# RUN ./waf install
# 
# WORKDIR /root
# RUN mkdir /root/.ndn/
# RUN cp /etc/ndn/client.conf.sample /root/.ndn/client.conf
# RUN chmod a+rwx /root/.ndn/client.conf



ENTRYPOINT tail -f /dev/null
#ENTRYPOINT nfd

#Build: docker build -t ndf .
#Run: docker run -i -t  ndf /bin/bash
# docker run --name ndf-inst -d ndf


#docker run --name nfd-inst -d nfd