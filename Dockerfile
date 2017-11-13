FROM ubuntu:16.04

RUN apt-get update
RUN apt-get -y install git python-pip

RUN git clone https://github.com/saltstack/salt.git

COPY version_check/ /

ENTRYPOINT ["python", "cli.py"]
