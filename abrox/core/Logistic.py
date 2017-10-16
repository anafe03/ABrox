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

        nCols = self.model_collection[0].scaled_simsum.shape[1]

        # init empty array to be filled
        X = np.empty(shape=(0,nCols))

        for model in self.model_collection:
            X = np.concatenate((X,model.scaled_simsum),axis=0)


        X = X[weights > 0, :]
        Y = Y[weights > 0]

        lreg = linear_model.LogisticRegression(solver="lbfgs")

        weights = weights[weights > 0]

        if X.shape[1] < 2:

            X = X.reshape(-1,1)

        if len(self.model_collection.obssum.shape) == 1:
            self.model_collection.obssum = self.model_collection.obssum.reshape(-1,1)

        model_probabilities = np.empty(len(self.model_collection))

        if len(np.unique(Y)) < 2:
            win = Y[0]
            lose = 1 - Y[0]
            model_probabilities[win] = 1
            model_probabilities[lose] = 0

        else:
            lreg.fit(X, Y, weights)
            model_probabilities = lreg.predict_proba(self.model_collection.obssum).flatten()

        for idx, model in enumerate(self.model_collection):
            model.accepted = model_probabilities[idx]
