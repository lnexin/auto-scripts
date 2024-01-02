FROM ubuntu:latest 
RUN apt-get update &&  \
    apt-get install -y openssh-server && \
    apt-get install -y openssh-client && \
    apt-get install -y vim && \
    mkdir /run/sshd
RUN echo 'root:password123.!' | chpasswd 
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config 
EXPOSE 22 
CMD ["/usr/sbin/sshd", "-D"]

