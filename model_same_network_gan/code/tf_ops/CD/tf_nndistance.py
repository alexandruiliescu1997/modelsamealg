import os
import tensorflow as tf

from tensorflow.python.framework import ops

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
nn_distance_module = tf.load_op_library(os.path.join(BASE_DIR, 'tf_nndistance_so.so'))


def nn_distance(xyz1, xyz2):
    """
        Computes the distance of nearest neighbors for a pair of point clouds
        input: xyz1: (batch_size,#points_1,3)  the first point cloud
        input: xyz2: (batch_size,#points_2,3)  the second point cloud
        output: dist1: (batch_size,#point_1)   distance from first to second
        output: idx1:  (batch_size,#point_1)   nearest neighbor from first to second
        output: dist2: (batch_size,#point_2)   distance from second to first
        output: idx2:  (batch_size,#point_2)   nearest neighbor from second to first
    """
    return nn_distance_module.nn_distance(xyz1, xyz2)


@ops.RegisterGradient('NnDistance')
def _nn_distance_grad(op, grad_dist1, grad_idx1, grad_dist2, grad_idx2):
    xyz1 = op.inputs[0]
    xyz2 = op.inputs[1]
    idx1 = op.outputs[1]
    idx2 = op.outputs[3]

    return nn_distance_module.nn_distance_grad(xyz1, xyz2, grad_dist1, idx1, grad_dist2, idx2)


if __name__ == '__main__':
    import time
    import random
    import numpy as np

    random.seed(100)
    np.random.seed(100)
    with tf.Session('') as sess:
        xyz1 = np.random.randn(32, 16384, 3).astype('float32')
        xyz2 = np.random.randn(32, 1024, 3).astype('float32')
        inp1 = tf.Variable(xyz1)
        inp2 = tf.constant(xyz2)
        reta, retb, retc, retd = nn_distance(inp1, inp2)
        loss = tf.reduce_sum(reta) + tf.reduce_sum(retc)
        train = tf.train.GradientDescentOptimizer(learning_rate=0.05).minimize(loss)
        sess.run(tf.global_variables_initializer())
        t0 = time.time()
        best = 1e100
        for i in range(100):
            trainloss, _ = sess.run([loss, train])
            newt = time.time()
            print(i, trainloss, (newt - t0) / (i + 1))
