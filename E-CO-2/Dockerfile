FROM ubuntu:16.04

MAINTAINER S. Koulouzis

##install java
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends openjdk-8-jdk
RUN apt-get upgrade -y
RUN apt-get install -y wget maven 

WORKDIR /root


RUN wget https://github.com/skoulouzis/E-CO-2/archive/v0.0.1.tar.gz
RUN tar -xzvf v0.0.1.tar.gz 
WORKDIR E-CO-2-0.0.1
RUN mvn install
WORKDIR rest
RUN mvn compile assembly:single

# RUN wget https://github.com/skoulouzis/E-CO-2/releases/download/v0.0.1/rest-1.0-SNAPSHOT-jar-with-dependencies.jar
# RUN wget https://github.com/skoulouzis/E-CO-2/releases/download/v0.0.1/configure.properties

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
ENTRYPOINT java -jar /root/E-CO-2-0.0.1/rest/target/rest-1.0-SNAPSHOT-jar-with-dependencies.jar /root/E-CO-2-0.0.1/etc/configure.properties 

# ENTRYPOINT java -jar rest-1.0-SNAPSHOT-jar-with-dependencies.jar /root/E-CO-2-0.0.1/etc/configure.properties 

# docker build -t e-co-2 .
# docker run --name e-co-2-inst -d e-co-2 -p 127.0.0.1:9999:9999