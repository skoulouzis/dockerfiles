FROM ubuntu:16.04

MAINTAINER S. Koulouzis
ARG RELESE_VERSION=0.0.2


##install java
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends openjdk-8-jdk
RUN apt-get upgrade -y
RUN apt-get install -y wget maven git 

WORKDIR /root
RUN mkdir workspace
WORKDIR workspace   
RUN wget https://github.com/skoulouzis/E-CO-2/archive/v$RELESE_VERSION.tar.gz
RUN tar -xzvf v$RELESE_VERSION.tar.gz
WORKDIR E-CO-2-$RELESE_VERSION
RUN mvn install
WORKDIR rest
RUN mvn compile assembly:single

# RUN git clone https://github.com/skoulouzis/E-CO-2.git
# WORKDIR E-CO-2
# RUN mvn install
# WORKDIR rest
# RUN mvn compile assembly:single

WORKDIR /root
RUN mkdir -p Downloads/classificationFiles/courseAvg
RUN mkdir -p Downloads/classificationFiles/cvProfile
RUN mkdir -p Downloads/classificationFiles/jobAvg
RUN mkdir -p Downloads/classificationFiles/course  
RUN mkdir -p Downloads/classificationFiles/cvAvg 
RUN mkdir -p Downloads/classificationFiles/cv
RUN mkdir -p Downloads/classificationFiles/jobProfile
RUN mkdir -p Downloads/classificationFiles/courseProfile
RUN mkdir -p Downloads/classificationFiles/job


EXPOSE 9999
ENTRYPOINT java -jar /root/workspace/E-CO-2-$RELESE_VERSION/rest/target/rest-1.0-SNAPSHOT-jar-with-dependencies.jar /root/workspace/E-CO-2-$RELESE_VERSION/etc/configure.properties 
# ENTRYPOINT tail -f /dev/null

# docker build -t e-co-2 .
# docker run -e RELESE_VERSION=0.0.2 --name e-co-2-inst -d e-co-2 -p 127.0.0.1:9999:9999