import tensorflow as tf
import os
import pyspark.sql.types as t
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("/Users/geminit/projects/HTSC-3.1/MNIST_data/", one_hot=True)

def compute(rdd):
    return [t.Row(userAdd='shanghai', userAge=20, userName='zhangsan', userSalary=13),
            t.Row(userAdd='beijin', userAge=30, userName='lisi', userSalary=15)]

