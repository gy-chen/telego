FROM ubuntu:cosmic

RUN apt-get update && \
  apt-get install -y libcaffe-cpu1 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

COPY ./build /pachi
WORKDIR /pachi
RUN ln -s /pachi/pachi /usr/local/bin/pachi

CMD pachi
