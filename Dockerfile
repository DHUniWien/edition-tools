FROM python:3
LABEL vendor=DHUniWien

# CollateX runtime dependencies and assorted necessary tools
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install \
    graphviz \
    openjdk-11-jre \
    pwgen \
    libxml2-utils \
    jq

# tpen-connect runtime dependencies and tpen2tei
RUN pip install \
    pyyaml \
    requests \
    requests-mock \
    bs4 \
    tpen2tei

# "Install" the tpen-connect utility, collatex, and the pipeline scripts
WORKDIR /root
COPY tools/src/tpen tpen
COPY tools/collatex.jar .
COPY scripts scripts
