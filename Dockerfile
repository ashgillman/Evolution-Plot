# -*- docker-image-name: "ashgillman/evolution-plot" -*-
FROM debian:jessie
MAINTAINER Ashley Gillman "ashley.gillman@uqconnect.edu.au"

RUN apt-get update && apt-get install -qy \
    graphviz \
    libgraphviz-dev \
    libyaml-dev \
    python3 \
    python3-pip
RUN pip3 install graphviz pyyaml

ADD . /app

ENTRYPOINT ["python3", "/app/evolution-plot.py"]
