import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras.layers import Conv2D, Dense, Flatten, Input, MaxPooling2D, UpSampling2D
from tensorflow.keras import Model
from tensorflow.keras.models import load_model

from gradient_accumulator import GradientAccumulateModel

from tests.utils import normalize_img, reset


def create_multi_input_output(image, label):
    return (image, image), (image, label)


def run_experiment(bs=16, accum_steps=4, epochs=1):
    # load dataset
    (ds_train, ds_test), ds_info = tfds.load(
        "mnist",
        split=["train", "test"],
        shuffle_files=True,
        as_supervised=True,
        with_info=True,
    )

    # get a smaller amount of samples for running the experiment
    ds_train = ds_train.take(1024)
    ds_test = ds_test.take(1024)

    # build train pipeline
    ds_train = ds_train.map(normalize_img)
    ds_train = ds_train.map(create_multi_input_output)
    ds_train = ds_train.batch(bs)
    ds_train = ds_train.prefetch(1)

    # build test pipeline
    ds_test = ds_test.map(normalize_img)
    ds_test = ds_test.map(create_multi_input_output)
    ds_test = ds_test.batch(bs)
    ds_test = ds_test.prefetch(1)

    # create multi-input multi-output model
    input1 = Input(shape=(28, 28, 1))
    input2 = Input(shape=(28, 28))

    x1 = Conv2D(8, (5, 5), activation="relu", padding="same")(input1)
    x1 = MaxPooling2D((2, 2))(x1)
    x1 = Conv2D(8, (5, 5), activation="relu", padding="same")(x1)
    x1 = UpSampling2D((2, 2))(x1)
    x1 = Conv2D(8, (5, 5), padding="same", name="reconstructor")(x1)

    x2 = Flatten()(input2)
    x2 = Dense(32, activation="relu")(x2)
    x2 = Dense(10, name="classifier")(x2)

    model = Model(inputs=[input1, input2], outputs=[x1, x2])

    # wrap model to use gradient accumulation
    if accum_steps > 1:
        model = GradientAccumulateModel(
            accum_steps=accum_steps, inputs=model.input, outputs=model.output
        )

    # compile model
    model.compile(
        optimizer=tf.keras.optimizers.SGD(1e-3),
        loss={
            "classifier": tf.keras.losses.SparseCategoricalCrossentropy(
                from_logits=True
            ),
            "reconstructor": "mse",
        },
        metrics={"classifier": tf.keras.metrics.SparseCategoricalAccuracy()},
    )

    # train model
    model.fit(
        ds_train,
        epochs=epochs,
        validation_data=ds_test,
    )

    model.save("./trained_model")

    # load trained model and test
    del model
    trained_model = load_model("./trained_model", compile=True)

    result = trained_model.evaluate(ds_test, verbose=1)
    print(result)

    return np.array(result)


def test_multitask():
    # set seed
    reset()

    # run once
    result1 = run_experiment(bs=32, accum_steps=1, epochs=1)

    # reset before second run to get reproducible results
    reset()

    # run again with different batch size and number of accumulations
    result2 = run_experiment(bs=16, accum_steps=2, epochs=1)

    # results should be "identical" (on CPU, can be different on GPU)
    np.testing.assert_almost_equal(result1, result2, decimal=3)
