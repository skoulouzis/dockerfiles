FROM ubuntu:latest


ENV DEBIAN_FRONTEND=noninteractive

#RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update && apt-get upgrade -y
RUN apt-get install swi-prolog -y
# RUN apt-get install build-essential autoconf curl chrpath pkg-config \
#         ncurses-dev libreadline-dev libedit-dev \
#         libunwind-dev \
#         libgmp-dev \
#         libssl-dev \
#         unixodbc-dev \
#         zlib1g-dev libarchive-dev \
#         libossp-uuid-dev \
#         libxext-dev libice-dev libjpeg-dev libxinerama-dev libxft-dev \
#         libxpm-dev libxt-dev \
#         libdb-dev \
#         openjdk-8-jdk junit wget -y
# 
# WORKDIR /root
# RUN wget www.swi-prolog.org/download/stable/src/swipl-7.4.0-rc1.tar.gz
# RUN tar zxvf swipl-7.4.0-rc1.tar.gz
# WORKDIR  swipl-7.4.0-rc1
# RUN cp -p build.templ build
# RUN sed -i -e 's#PREFIX=$HOME#PREFIX=/usr/local#g' build
# RUN ./build
RUN prolog --version





