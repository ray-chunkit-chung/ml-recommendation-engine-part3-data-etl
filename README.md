# ml-recommendation-engine-part3-data-etl

<https://neptune.ai/blog/training-models-on-streaming-data>

<https://neptune.ai/blog/etl-in-machine-learning>

## Install packages

### Python

```bash
cd /tmp
wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz
tar -xzvf Python-3.11.5.tgz
cd Python-3.11.5/
apt update
apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev graphviz
./configure --enable-optimizations --enable-loadable-sqlite-extensions
make -j `nproc`
make altinstall
# ln -s /usr/local/bin/python3.11 /usr/local/bin/python
cd /com.docker.devenvironments.code
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Kafka

```bash
apt -y install default-jre
curl -sSOL https://downloads.apache.org/kafka/3.5.1/kafka_2.13-3.5.1.tgz
tar -xzf kafka_2.13-3.5.1.tgz

# server.properties > listeners=PLAINTEXT://127.0.0.1:9092
# ./kafka_2.13-3.5.1/bin/zookeeper-server-start.sh -daemon ./kafka_2.13-3.5.1/config/zookeeper.properties
# ./kafka_2.13-3.5.1/bin/kafka-server-start.sh -daemon ./kafka_2.13-3.5.1/config/server.properties
./kafka_2.13-3.5.1/bin/zookeeper-server-start.sh ./kafka_2.13-3.5.1/config/zookeeper.properties
./kafka_2.13-3.5.1/bin/kafka-server-start.sh ./kafka_2.13-3.5.1/config/server.properties
```

## Create Kafka topics

For training and testing data

```bash
./kafka_2.13-3.5.1/bin/kafka-topics.sh --create --bootstrap-server 127.0.0.1:9092 --replication-factor 1 --partitions 1 --topic train
./kafka_2.13-3.5.1/bin/kafka-topics.sh --create --bootstrap-server 127.0.0.1:9092 --replication-factor 1 --partitions 2 --topic test
```



## dynamic embeddings

https://blog.tensorflow.org/2023/04/training-recommendation-model-with-dynamic-embeddings.html

