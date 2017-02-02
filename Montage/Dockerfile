FROM ubuntu:latest

MAINTAINER S. Koulouzis

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && apt-get upgrade -y
RUN apt-get install wget build-essential -y

WORKDIR /root
RUN pwd


RUN wget http://montage.ipac.caltech.edu/download/Montage_v5.0.tar.gz
RUN tar -xzf Montage_v5.0.tar.gz
RUN ls
WORKDIR Montage
RUN make

RUN mkdir examples
COPY pleiades.sh examples
COPY pleiades.hdr examples
COPY downloadDSS.sh examples


ENV PATH=$PATH:/root/Montage/bin
RUN echo PATH=$PATH:/root/Montage/bin >> /etc/profile
RUN echo PATH=$PATH:/root/Montage/examples >> /etc/profile
RUN source /etc/profile

 
RUN echo PATH=$PATH:/root/Montage/bin >> /root/.bashrc 
RUN echo PATH=$PATH:/root/Montage/examples >> /root/.bashrc
RUN source /root/.bashrc

RUN mArchiveList

WORKDIR examples
RUN chmod +x *.sh
RUN ./downloadDSS.sh
      
ENTRYPOINT sh pleiades.sh
