FROM ubuntu:18.04

RUN apt-get update
RUN apt-get -y install git python3-pip

RUN git clone https://github.com/saltstack/salt.git

COPY version_check/ /

ENTRYPOINT ["python3", "cli.py"]

