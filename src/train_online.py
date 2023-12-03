import os
import pandas as pd

from tensorflow.keras.layers import (
    Input,
    IntegerLookup,
    Embedding,
    Flatten,
    Dot,
)
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


DIRNAME = os.path.dirname(__file__)
TRAIN_PATH = os.path.join(DIRNAME, "../local/train.csv")
TEST_PATH = os.path.join(DIRNAME, "../local/test.csv")
MODEL_PATH = os.path.join(DIRNAME, "../local/model.h5")


def load_model():
    """
    A dummy pre-trained model for testing purposes.
    """
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
    user_embedding = Embedding(input_dim=len(all_users) + 1, output_dim=32)(
        user_as_integer
    )
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

    return model


def main():
    # A dummy pre-trained model
    model = load_model()

    # Load a small batch of data
    train = pd.read_csv(TRAIN_PATH, nrows=10000)
    test = pd.read_csv(TEST_PATH, nrows=10000)

    # Train the model
    early_stop = EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True
    )
    checkpoint = ModelCheckpoint(MODEL_PATH, monitor="val_loss", save_best_only=True)
    model.fit(
        [train["user_id"], train["movie_id"]],
        train["user_rating"],
        epochs=10,
        batch_size=64,
        validation_split=0.2,
        callbacks=[early_stop, checkpoint],
    )


if __name__ == "__main__":
    main()
