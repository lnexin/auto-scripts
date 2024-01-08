FROM nginx:latest
RUN apt-get update &&  \
    apt-get install -y vim && \
EXPOSE 22 
CMD ["/usr/sbin/sshd", "-D"]

