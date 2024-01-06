from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from kafka import KafkaProducer
import tensorflow_datasets as tfds
import socket
import os

REGION = 'ap-southeast-2'
BOOTSTRAP_SERVERS = [
      'xxxxx'
]

class MSKTokenProvider():
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token(REGION)
        return token

def error_callback(exc):
      raise Exception('Error while sending data to kafka: {0}'.format(str(exc)))


tp = MSKTokenProvider()

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    security_protocol='SASL_SSL',
    sasl_mechanism='OAUTHBEARER',
    sasl_oauth_token_provider=tp,
    client_id=socket.gethostname(),
)

data = tfds.load("movielens/1m-ratings")

df = tfds.as_dataframe(data["train"])

filtered_data = (
    df.filter(["timestamp", "user_id", "movie_id", "user_rating"])
    .sort_values("timestamp")
    .astype({"user_id": int, "movie_id": int, "user_rating": int})  # nicer types
    .drop(columns=["timestamp"])  # don't need the timestamp anymore
)

# We will also keep the timestamp to conduct a temporal train-test split since
#  this resembles how we train in real life: we train now, but we want the model
# to work well tomorrow. So we should evaluate the model quality like this as well.
train = filtered_data.iloc[:900000]  # chronologically first 90% of the dataset
test = filtered_data.iloc[900000:]  # chronologically last 10% of the dataset

if not os.path.isdir("../local"):
    os.mkdir("../local")

if not os.path.isfile("../local/train.csv"):
    train.to_csv("../local/train.csv", index=False)

if not os.path.isfile("../local/test.csv"):
    test.to_csv("../local/test.csv", index=False)

x_train = list(filter(None, train[["user_id","movie_id"]].to_csv(index=False).split("\n")[1:]))
y_train = list(filter(None, train[["user_rating"]].to_csv(index=False).split("\n")[1:]))
x_test = list(filter(None, test[["user_id","movie_id"]].to_csv(index=False).split("\n")[1:]))
y_test = list(filter(None, test[["user_rating"]].to_csv(index=False).split("\n")[1:]))


def write_to_kafka(topic_name, items):
      count=0
      for message, key in items:
        print(message.encode('utf-8'))
        producer.send(topic_name,
                      key=key.encode('utf-8'),
                      value=message.encode('utf-8')).add_errback(error_callback)
        count+=1
      producer.flush()
      print("Wrote {0} messages into topic: {1}".format(count, topic_name))


write_to_kafka("MSKTutorialTopic", zip(x_train, y_train))
print(v)
