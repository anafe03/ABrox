import numpy as np


def get_summary_statistic(version):
    if version == "cohen_d":
        def summary(data):
            v1, v2 = data
            diff_means = np.mean(v1) - np.mean(v2)
            overall_std = (np.std(v1) + np.std(v2)) / 2
            return diff_means / overall_std

    if version == "levene":
        def summary(data):
            v1, v2 = data
            trans_v1, trans_v2 =
            np.abs(v1 - np.mean(v1)), np.abs(v2 - np.mean(v2))
            diff_means = np.mean(trans_v1) - np.mean(trans_v2)
            return diff_means
