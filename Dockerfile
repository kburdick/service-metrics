FROM ubuntu:latest

RUN apt-get update
RUN apt-get install software-properties-common --yes
RUN apt-get install build-essential wget -y
RUN apt-get install python3-pip -y
RUN pip install --upgrade pip

WORKDIR /opt/serviceMetrics

COPY ./requirements.txt /opt/serviceMetrics/.
COPY ./serviceMetrics.py /opt/serviceMetrics/.

RUN python3 -m pip install -r /opt/serviceMetrics/requirements.txt

CMD ["python3", "serviceMetrics.py"]