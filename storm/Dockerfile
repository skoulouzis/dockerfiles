FROM storm:1.2.1
MAINTAINER S. Koulouzis 


RUN apk add --no-cache --virtual .build-deps screen
RUN apk del openjdk8-jre
RUN apk add --update bash && rm -rf /var/cache/apk/*

ENV JAVA_VERSION=8  \
    JAVA_UPDATE=151 \
    JAVA_BUILD=12 \
    JAVA_HOME="/usr/lib/jvm/default-jvm" \
    LANG=C.UTF-8 \
    GLIBC_VERSION=2.27-r0 \
    ORACLE_AUTHORIZATION_KEY=e758a0de34e24606bca991d704f6dcbf


RUN apk upgrade --update && apk add --no-cache --virtual=build-dependencies libstdc++ curl ca-certificates unzip

RUN curl -Ls https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.27-r0/glibc-2.27-r0.apk > /tmp/glibc-2.27-r0.apk
RUN apk add --allow-untrusted /tmp/glibc-2.27-r0.apk 
RUN  rm -v /tmp/*.apk
RUN ( /usr/glibc-compat/bin/localedef --force --inputfile POSIX --charmap UTF-8 C.UTF-8 || true )
RUN echo "export LANG=C.UTF-8" > /etc/profile.d/locale.sh  
RUN echo 'hosts: files mdns4_minimal [NOTFOUND=return] dns mdns4' >> /etc/nsswitch.conf  && \
    wget --header "Cookie: oraclelicense=accept-securebackup-cookie" https://github.com/QCAPI-DRIP/DRIP-integration/releases/download/0.2.1/jdk-8u151-linux-x64.tar.gz -O /tmp/java.tar.gz 
        
RUN gunzip /tmp/java.tar.gz && \
    tar -C /tmp -xf /tmp/java.tar && \
    mkdir -p "/usr/lib/jvm"    
    
RUN mv "/tmp/jdk1.${JAVA_VERSION}.0_${JAVA_UPDATE}" "/usr/lib/jvm/java-${JAVA_VERSION}-oracle" && \
    rm -rf "${JAVA_HOME}" && \
    ln -s "java-${JAVA_VERSION}-oracle" "$JAVA_HOME" && \
    ln -s "$JAVA_HOME/bin/"* "/usr/bin/" && \
    rm -rf "$JAVA_HOME/"*src.zip \
            "$JAVA_HOME/lib/missioncontrol" \
            "$JAVA_HOME/lib/visualvm" \
            "$JAVA_HOME/lib/"*javafx* \
            "$JAVA_HOME/jre/lib/ext/jfxrt.jar" \
            "$JAVA_HOME/jre/bin/javaws" \
            "$JAVA_HOME/jre/lib/javaws.jar" \
            "$JAVA_HOME/jre/lib/desktop" \
            "$JAVA_HOME/jre/plugin" \
            "$JAVA_HOME/jre/lib/"deploy* \
            "$JAVA_HOME/jre/lib/"*javafx* \
            "$JAVA_HOME/jre/lib/"*jfx* \
            "$JAVA_HOME/jre/lib/amd64/libdecora_sse.so" \
            "$JAVA_HOME/jre/lib/amd64/"libprism_*.so \
            "$JAVA_HOME/jre/lib/amd64/libfxplugins.so" \
            "$JAVA_HOME/jre/lib/amd64/libglass.so" \
            "$JAVA_HOME/jre/lib/amd64/libgstreamer-lite.so" \
            "$JAVA_HOME/jre/lib/amd64/"libjavafx*.so \
            "$JAVA_HOME/jre/lib/amd64/"libjfx*.so \
            "$JAVA_HOME/jre/bin/jjs" \
            "$JAVA_HOME/jre/bin/keytool" \
            "$JAVA_HOME/jre/bin/orbd" \
            "$JAVA_HOME/jre/bin/pack200" \
            "$JAVA_HOME/jre/bin/policytool" \
            "$JAVA_HOME/jre/bin/rmid" \
            "$JAVA_HOME/jre/bin/rmiregistry" \
            "$JAVA_HOME/jre/bin/servertool" \
            "$JAVA_HOME/jre/bin/tnameserv" \
            "$JAVA_HOME/jre/bin/unpack200" \
            "$JAVA_HOME/jre/lib/ext/nashorn.jar" \
            "$JAVA_HOME/jre/lib/jfr.jar" \
            "$JAVA_HOME/jre/lib/jfr" \
            "$JAVA_HOME/jre/lib/oblique-fonts"    
RUN apk del build-dependencies && \
    rm -rf /tmp/* /var/cache/apk/*            
    


# WORKDIR /
# RUN git clone https://github.com/Blackmist/SubmitToNimbus.git
# WORKDIR SubmitToNimbus
# RUN mvn package
WORKDIR /

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]




#sudo docker build -t storm-submitter .