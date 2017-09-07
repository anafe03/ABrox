import numpy as np


def get_distance(version):
    if version == "euclidean":
        def distance(a, b):
            return np.linalg.norm(a - b)
        return distance
