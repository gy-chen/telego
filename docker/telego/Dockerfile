FROM gychen/pachi

RUN apt-get update && \
  apt-get install -y python3 python3-pip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

COPY ./telego /app
WORKDIR /app

RUN pip3 install Babel && pip3 install .
CMD telego
