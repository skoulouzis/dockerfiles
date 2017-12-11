FROM buildpack-deps:jessie

RUN apt-get update

# Common dependencies and setup, omitting stuff already included in 'buildpack-deps':
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y libpcap-dev libcrypto++-dev libboost-all-dev

# Missing dependencies: http://redmine.named-data.net/issues/2013
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y procps psmisc sudo

RUN mkdir -p /scripts /source

ADD ./scripts/install-ndn-cxx.sh /scripts/
RUN /scripts/install-ndn-cxx.sh

# ADD ./scripts/install-nfd.sh /scripts/
# RUN /scripts/install-nfd.sh

WORKDIR /root
RUN git clone --depth 1 --recursive https://github.com/felixrabe/NFD.git
WORKDIR NFD
RUN git checkout -b origin/ndn-start-fg
# RUN ./waf configure
# RUN ./waf
# RUN ./waf install
 
# RUN cp /usr/local/etc/ndn/nfd.conf.sample /usr/local/etc/ndn/nfd.conf
# CMD /usr/local/bin/nfd-start-fg