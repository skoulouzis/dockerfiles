FROM storm:1.2.1
MAINTAINER S. Koulouzis 


RUN apk add --no-cache --virtual .build-deps screen;
# 
# WORKDIR /
# RUN git clone https://github.com/Blackmist/SubmitToNimbus.git
# WORKDIR SubmitToNimbus
# RUN mvn package
WORKDIR /

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]




#sudo docker build -t docker-storm .