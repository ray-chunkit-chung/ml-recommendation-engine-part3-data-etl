import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import (
    Input,
    IntegerLookup,
    Embedding,
    Flatten,
    Dot,
)
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

TRAIN_PATH = "../local/train.csv"
TEST_PATH = "../local/test.csv"
MODEL_PATH = "../local/model.h5"

# Load the MovieLens dataset (you can replace it with your own data)
# Assuming you have a CSV file with columns: 'user_id', 'movie_id', 'rating'
train = pd.read_csv(TRAIN_PATH)
test = pd.read_csv(TEST_PATH)

# Unique users and movies
all_users = train["user_id"].unique()
all_movies = train["movie_id"].unique()

# Create user and movie input layers
user_input = Input(shape=(1,), name="user_input")
movie_input = Input(shape=(1,), name="movie_input")

# Create user and movie IntegerLookup
user_as_integer = IntegerLookup(vocabulary=all_users)(user_input)
movie_as_integer = IntegerLookup(vocabulary=all_movies)(movie_input)

# Create user and movie embeddings
user_embedding = Embedding(input_dim=len(all_users) + 1, output_dim=32)(user_as_integer)
movie_embedding = Embedding(input_dim=len(all_movies) + 1, output_dim=32)(
    movie_as_integer
)

# Create the recommendation model (dot product of user and movie embeddings)
dot_product = Dot(axes=2)([user_embedding, movie_embedding])

# Flatten the dot_product
flatten = Flatten()(dot_product)

# Build and compile the model
model = Model(inputs=[user_input, movie_input], outputs=flatten)
model.compile(loss="mean_squared_error", optimizer="adam")

# Train the model
early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
checkpoint = ModelCheckpoint(MODEL_PATH, monitor="val_loss", save_best_only=True)
model.fit(
    [train["user_id"], train["movie_id"]],
    train["user_rating"],
    epochs=10,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stop, checkpoint],
)

# Evaluate the model
loss = model.evaluate([test["user_id"], test["movie_id"]], test["user_rating"])
print(f"Test Loss: {loss}")



import tensorflow_io as tfio

BATCH_SIZE=64
SHUFFLE_BUFFER_SIZE=64
NUM_COLUMNS = 2

online_train_ds = tfio.experimental.streaming.KafkaBatchIODataset(
    topics=["train"],
    group_id="cgonline",
    servers="127.0.0.1:9092",
    stream_timeout=10000, # in milliseconds, to block indefinitely,set it -1
    configuration=[
        "session.timeout.ms=7000",
        "max.poll.interval.ms=8000",
        "auto.offset.reset=earliest"
    ],
)

def decode_kafka_item(item):
      message = tf.io.decode_csv(item.message,
                                [[0.0] for i in range(NUM_COLUMNS)])
      key = tf.strings.to_number(item.key)
      return (message, key)

def decode_kafka_online_item(raw_message, raw_key):
    message = tf.io.decode_csv(raw_message, [[0.0] for i in range(NUM_COLUMNS)])
    key = tf.strings.to_number(raw_key)
    return (message, key)
 
for mini_ds in online_train_ds:
    mini_ds = mini_ds.shuffle(buffer_size=32)
    mini_ds = mini_ds.map(decode_kafka_online_item)
    mini_ds = mini_ds.batch(32)
    if len(mini_ds) > 0:
      model.fit(mini_ds, epochs=3)

train_ds = tfio.IODataset.from_kafka('cancer-train', partition=0, offset=0)
train_ds = train_ds.shuffle(buffer_size=SHUFFLE_BUFFER_SIZE)
train_ds = train_ds.map(decode_kafka_item)
train_ds = train_ds.batch(BATCH_SIZE)

