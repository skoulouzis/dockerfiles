FROM ubuntu:16.04


#install openssh and wget
RUN apt-get update && apt-get install -y openssh-server

RUN mkdir /var/run/sshd
RUN echo 'root:screencast' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

RUN adduser --disabled-password --gecos '' vm_user
WORKDIR /home/vm_user/
COPY id_rsa.pub /home/vm_user/
RUN mkdir .ssh/
RUN chmod 700 .ssh/
RUN cat id_rsa.pub >> .ssh/authorized_keys
RUN chown -R vm_user .ssh


EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

# ENTRYPOINT tail -f /dev/null 
#Build: docker build -t ubunut_node .
# Run: sudo docker run -i -t  ubunut_node /bin/bash


