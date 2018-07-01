git clone --depth=1 https://github.com/pasky/pachi || (cd pachi ; git pull)
docker build -t pachi-build -f Dockerfile.build .
docker container create --name pachi-build pachi-build
docker container start pachi-build
docker container cp pachi-build:/build .
docker container rm -f pachi-build

curl http://physik.de/CNNlast.tar.gz > CNNlast.tar.gz && tar -zxf CNNlast.tar.gz
cp ./golast* ./build
docker build -t pachi .
