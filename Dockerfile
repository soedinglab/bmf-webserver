FROM ubuntu:20.10

WORKDIR /code

RUN apt-get update 
RUN apt-get install --yes bash default-mysql-client libmariadb3 supervisor g++ python3 python3-pip
RUN apt-get install --yes libmariadb-dev-compat libopenblas-dev wget zip

# install python dependencies
COPY requirements.txt /code/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY bmf_tool-1.0.0.tar.gz /code/
RUN pip3 install /code/bmf_tool-1.0.0.tar.gz

# use a cool init system for handing signals: https://github.com/Yelp/dumb-init
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN mkdir /code/media/

ENV PYTHONUNBUFFERED 1