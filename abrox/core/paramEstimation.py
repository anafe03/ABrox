import numpy as np
import statsmodels.api as sm


class ParamEstimator:
    """
    Implements the regression-based ABC for parameter estimation
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
        """ Run weighted linear regression and adjust parameters"""

        weights = self.computeWeights()
        X = self.model_collection[0].scaled_simsum[weights > 0, :]
        print("X shape: {}".format(X.shape))
        X = sm.add_constant(X)

        # NxM posterior matrix containing len(Y) rows and nparams columns

        nparams = len(self.model_collection[0].parameterList[0])
        print("number of parameters: {}".format(nparams))
        postMat = np.empty(shape=(X.shape[0], nparams))
        for idx in range(nparams):
            Y = np.array([paramSample[idx]
                          for paramSample in self.model_collection[0].parameterList])

            print("Mean of param: {}".format(np.mean(Y)))

            Y = Y[weights > 0]

            wls_model = sm.WLS(Y, X, weights=weights[weights > 0])
            fit = wls_model.fit()

            nFeatures = 1 + self.model_collection.obssum.shape[1]
            prediction = fit.predict(np.append(1,self.model_collection.obssum).reshape(1,nFeatures))
            resid = fit.resid
            postMat[:, idx] = prediction + resid

        return postMat
