import numpy as np
from sklearn import linear_model
from sklearn.model_selection import KFold


class Logistic:
    """
    Implements the regression-based ABC for model comparison
    based on logistic (multinomial) regression
    """

    def __init__(self, model_collection):
        self.model_collection = model_collection

    def computeWeights(self):
        """Compute weights according to Epanechnikov kernel"""
        threshold_array = [self.model_collection.threshold] * len(self.model_collection.distances)
        weights = [(1 / e) * (1 - (t / e)**2) if t <= e else 0
                   for t, e in zip(self.model_collection.distances, threshold_array)]
        return np.array(weights)

    def run(self):
        """ Run weighted logistic regression and adjust parameters"""

        weights = self.computeWeights()

        model_indices = np.arange(len(self.model_collection))

        N = []
        for model in self.model_collection:
            N.append(len(model.scaled_simsum))

        Y = np.repeat(model_indices, N)
        print(Y)
        # X = np.zeroes(shape=(Y.shape[0], len(self.model_collection)))

        # for i, model in enumerate(self.model_collection):
        #     X[:, i] = model.scaled_simsum

        print("Scaled simsum shape: {}".format(self.model_collection[0].scaled_simsum.shape))

        X = np.append(self.model_collection[0].scaled_simsum,
                      self.model_collection[1].scaled_simsum)

        dat = np.column_stack((X, Y))
        dat = dat[weights > 0, :]

        lreg = linear_model.LogisticRegression(solver="lbfgs")

        weights = weights[weights > 0]

        # kf = KFold(n_splits=5, shuffle=True)
        # for idx, blub in kf.split(dat):
        #     dat_sub = dat[idx]
        #     lreg.fit(dat_sub[:, 0].reshape(-1, 1), dat_sub[:, 1], weights[idx])
        #     print(lreg.predict_proba([self.model_collection.obssum]))

        lreg.fit(dat[:, 0].reshape(-1, 1), dat[:, 1], weights)
        model_probabilities = lreg.predict_proba([self.model_collection.obssum]).flatten()
        for idx, model in enumerate(self.model_collection):
            model.accepted = model_probabilities[idx]
