FROM ubuntu:latest

MAINTAINER S. Koulouzis

ENV DEBIAN_FRONTEND=noninteractive

# RUN add-apt-repository ppa:ubuntu-lxc/lxd-stable
RUN apt-get update && apt-get upgrade -y
RUN apt-get install golang git -y
RUN mkdir /root/go
ENV GOPATH=/root/go
RUN echo $GOPATH
RUN go get github.com/tylertreat/flotilla/flotilla-server
RUN go get github.com/tylertreat/flotilla/flotilla-client
RUN flotilla-server
RUN flotilla-client --broker=rabbitmq


