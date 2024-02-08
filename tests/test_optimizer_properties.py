import pytest
import tensorflow as tf
from gradient_accumulator import GradientAccumulateOptimizer
from .utils import get_opt

tf_version = int(tf.version.VERSION.split(".")[1])


@pytest.fixture
def optimizer():
    opt = get_opt(opt_name="SGD", tf_version=tf_version)
    return GradientAccumulateOptimizer(optimizer=opt, accum_steps=2)

def test_learning_rate_getter(optimizer):
    assert optimizer.learning_rate == 0.01

def test_learning_rate_setter(optimizer):
    optimizer.learning_rate = 0.02
    assert optimizer.learning_rate == 0.02

def test_lr_getter(optimizer):
    assert optimizer.lr == 0.01

def test_lr_setter(optimizer):
    optimizer.lr = 0.02
    assert optimizer.lr == 0.02

def test__learning_rate(optimizer):
    assert optimizer._learning_rate == 0.01
    optimizer.learning_rate = 0.02
    assert optimizer._learning_rate == 0.02

def test_reset_single_gradient(optimizer):
    var = tf.Variable([1.0, 2.0], dtype=tf.float32)
    optimizer.add_slot(var, "ga", initializer=tf.constant([3.0, 4.0]))
    gradient = optimizer.get_slot(var, "ga")
    optimizer._reset_single_gradient(gradient)
    assert tf.reduce_all(tf.equal(gradient, tf.zeros_like(gradient)))

def test_reset(optimizer):
    var1 = tf.Variable([1.0, 2.0], dtype=tf.float32)
    var2 = tf.Variable([3.0, 4.0], dtype=tf.float32)
    optimizer.add_slot(var1, "ga", initializer=tf.constant([5.0, 6.0]))
    optimizer.add_slot(var2, "ga", initializer=tf.constant([7.0, 8.0]))
    for var in [var1, var2]:
        gradient = optimizer.get_slot(var, "ga")
        assert tf.reduce_all(tf.equal(gradient, tf.zeros_like(gradient))).numpy() == False

    optimizer.reset()
    for var in [var1, var2]:
        gradient = optimizer.get_slot(var, "ga")
        assert tf.reduce_all(tf.equal(gradient, tf.zeros_like(gradient))).numpy() == True