from random import randrange
import numpy as np
import itertools
import pickle
import os

from .model import Model

# =======================================#
# Model Collection class
# =======================================#


class ModelCollection(list):
    """Population of particles for all given models."""

    def __init__(self, user_models):
        super().__init__(Model(user_model) for user_model in user_models)
        self.simsum = self.create_dict()
        self.obssum = None
        self.distances = None
        self.percentile = None

    def sample_index(self):
        """Sample a model index."""
        return randrange(len(self))

    def create_dict(self):
        """
        Create empty dict with keys equal to the model indices (for parameter
        estimation the dict has only one key). The values of the keys are lists
        containing the simulated summary statitics for the models.
        """
        model_indices = list(range(0, len(self)))
        return {key: [] for key in model_indices}

    def create_particle(self, model_index):
        """Main function"""
        # choose model index
        # model_index = self.sample_index()
        # pick model based on index
        model = self[model_index]
        # sample parameter bundle from model paramater priors
        param = model.sample_parameter()
        # simulate data
        simdata = model.simulate(param)
        # compute summary of simulated data
        sim_summary = model.summary(simdata)
        # compute distance

        return model_index, param, sim_summary

    def transfer(self,
                 model_index=None,
                 simsum=None,
                 param=None):
        """Add necessary information."""
        self.simsum[model_index].append(simsum)
        self[model_index].add_parameter(list(param.values()))

    def scale(self):
        """
        Scale summary statistics and pass the scaled statistics to
        each model. Computes the distances for each simulated dataset.
        """
        # Store all summary statistics in one large list.
        sumstats = []
        for sumstat in self.simsum.values():
            sumstats += sumstat

        # if summary statistics is multi-dimensional
        if type(sumstats[0]) is np.ndarray:
            sumstats = np.array(sumstats)

        # else if scalar, reshape to array with one column
        else:
            sumstats = np.array(sumstats).reshape(-1, 1)

        # iterate over columns of array and scale
        MAD = np.empty(sumstats.shape[1])
        for idx, sum_stat in enumerate(sumstats.T):
            Median = np.median(sum_stat)
            MAD[idx] = np.median([np.abs(x - Median) for x in sum_stat])
            sumstats[:, idx] = sum_stat / MAD[idx]

        # scale observed summary statistics by each MAD
        self.obssum = np.array([self.obssum]) / MAD
        # print("Observed summary stat: {}".format(self.obssum))

        for model in self:
            model.scaled_obssum = self.obssum

        return sumstats

    def computeDistance(self, sumstats):
        """
        Compute the distance between observed and simulated summary stats
        """
        self.distances = np.array([self[0].compute_distance(simsum, self.obssum)
                                   for simsum in sumstats])

    def passToModel(self, sumstats):
        """
        Pass the simulated summary statistics from each model to this model.
        """
        split_sumstats = np.split(sumstats, len(self))
        # pass scaled simulated summary statistics to each model
        for idx, model in enumerate(self):
            model.scaled_simsum = split_sumstats[idx]

    def computeThreshold(self):
        """ Compute threshold value based on percentile specified by user"""
        self.threshold = np.percentile(self.distances, q=self.percentile * 100)

    def computeAcceptance(self):
        """ Split distances and compute how many distances are below
        the threshold for each model. Store the number."""
        split_distances = np.split(self.distances, len(self))
        for idx, model in enumerate(self):
            model.accepted = np.sum(
                [distance < self.threshold
                 for distance in split_distances[idx]])

    def bayesFactor(self):
        """ Compute the Bayes Factor as ratio of accepted simulations."""
        model_sizes = [model.accepted for model in self]
        nModels = len(model_sizes)
        tril = [b / a for a, b in list(itertools.combinations(model_sizes, 2))]

        triu = []
        for t in tril:
            try:
                inverse = 1 / t
                triu.append(inverse)
            except ZeroDivisionError:
                triu.append(np.inf)

        # triu = [1 / t for t in tril]

        bfMatrix = np.ones((nModels, nModels))

        bfMatrix[np.tril_indices(nModels, -1)] = tril
        bfMatrix[np.triu_indices(nModels, 1)] = triu

        return bfMatrix

    def descriptives(self, postMatrix):
        """
        Return matrix of means and standard deviations for
        each parameter posterior distribution
        """
        nparams = postMatrix.shape[1]
        out = np.empty(shape=(2, nparams))
        means = np.mean(postMatrix, axis=0)
        stds = np.std(postMatrix, axis=0)
        out[0, :] = means
        out[1, :] = stds
        return out

    def saveResults(self, diff_time, threshold,  outdir, method=None, postMatrix=None):
        """Save results in dict and pickle"""
        resDict = {'time (s)': round(diff_time), 'threshold': round(threshold)}

        if method is None:
            resDict['posterior'] = {}
            for i, col in enumerate(postMatrix.T):
                resDict['posterior'][str(i)] = col.tolist()


        else:
            for model in self:
                resDict[model.name] = {}
                if method == 'rejection':
                    resDict[model.name]['samples'] = model.accepted
                if method == 'logistic':
                    resDict[model.name]['probability'] = round(model.accepted,3)

            bf = np.around(self.bayesFactor(),decimals=3).tolist()

            resDict['bf'] = bf

        pickle.dump(resDict, open(os.path.join(outdir, "save.p"), "wb"))
        return resDict

    def report(self, diff_time, threshold, method=None, postMatrix=None):

        if method is None:  # parameter estimation
            descriptives = self.descriptives(postMatrix)

            print("Mean and SD:\n {}".format(descriptives))

        else:

            for model in self:
                if method == "rejection":
                    print("{} was sampled {} times".
                          format(model.name, model.accepted))

                if method == "logistic":
                    print("Model probability of {} = {}".
                          format(model.name, model.accepted))

            bf = self.bayesFactor()
            print("\nApproximate Bayes Factor Matrix: \n{}".
                  format(np.around(bf, 2)))
