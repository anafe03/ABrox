import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf

from abrox.core.abc_utils import toArray, euclideanDistance


class ABCCv:

    def __init__(self, refTable, keep, objective, times, modelNames=None):
        self.estimatedParams = None
        self.trueParams = None
        self.refTable = refTable
        self.sumStatArray = toArray(self.refTable,'sumstat')
        self.paramArray = toArray(self.refTable,'param')
        self.indexList = np.arange(len(self.refTable.index))
        self.picks = []
        self.keep = keep
        self.objective = objective
        self.times = times
        self.modelNames = modelNames

    def _getRandomIndices(self):
        """
        Pick a random row index from the reference table and the remaining indices.
        :return: both the picked index and the remaining indices.
        """
        picked = np.random.choice(self.indexList)

        self.picks.append(picked)

        notPicked = self.indexList[self.indexList != picked]
        return picked, notPicked

    def calculateDistance(self, picked, notPicked):
        """
        Compute distances between all simulated summary statistics and
        the pseudo-observed summary statistic
        :return: distances (one less then the number of rows of refTable)
        """
        distances = euclideanDistance(self.sumStatArray[notPicked], self.sumStatArray[picked])
        return distances

    def deletePickedRow(self,picked):
        """
        Drop the picked row from the reference table.
        :param picked: integer representing the row-index.
        :return: None
        """
        subTable = self.refTable.drop(self.refTable.index[[picked]], inplace=False)
        return subTable

    def getSubset(self, subTable):
        """
        Return tuple with filtered Reference Table only containing
        rows for which the distance is < threshold and threshold itself.
        :return: the tuple
        """
        q = self.keep / len(subTable.index) * 100
        threshold = np.percentile(subTable['distance'],q=q)
        subset = subTable[subTable['distance'] < threshold]
        return subset

    def getEstimates(self,subset):
        """
        Compute mean for each parameter in subset.
        :param subset: the subset table.
        :return: the means (estimates)
        """
        paramArray = toArray(subset,'param')
        return np.mean(paramArray, axis=0)

    def getPrediction(self,subset):
        """
        Return a prediction (model index) based on a subset of the reference table.
        :param subset: the subset of the ref table.
        :return: a prediction
        """
        _ , counts = np.unique(subset['idx'], return_counts=True)
        return np.argmax(counts)

    def computeSubset(self):
        """
        Run cross validation scheme:
            - pick a simulated summary statistic from the ref table.
            - treat it as pseudo-observed
            - compute the distances between all other and the pseudo-observed one.
            - compute subset reference table based on distances.
        :param times: accuracy of cv.
        :return: subset reference table.
        """

        picked, notPicked = self._getRandomIndices()
        distances = self.calculateDistance(picked, notPicked)
        subTable = self.deletePickedRow(picked)
        subTable['distance'] = distances
        filteredSubset = self.getSubset(subTable)

        return filteredSubset

    def compute(self):
        """
        Compute the array of estimated parameters if obj is inference.
        Compute the model predictions if obj is comparison.
        :param times: accuracy of cross validation sheme.
        """
        if self.objective == "comparison":

            pred = np.empty(shape=(self.times,1),dtype=np.uint8)

            for i in range(self.times):
                subset = self.computeSubset()
                pred[i,0] = self.getPrediction(subset)

            return pred

        if self.objective == "inference":

            cols = len(self.refTable.at[0, 'param'])
            estimatedParams = np.empty(shape=(self.times, cols))

            for i in range(self.times):
                subset = self.computeSubset()
                estimatedParams[i, :] = self.getEstimates(subset)

            return estimatedParams

    def report(self, outputdir):
        """
        Compute the prediction error if the objective is inference.
        Compute the confusion matrix if the objective is comparison.
        """

        if self.objective == "comparison":
            predictions = self.compute()
            true = toArray(self.refTable, 'idx')[self.picks, :]
            actual = pd.Series(true[:,0],name="Actual")
            predicted = pd.Series(predictions[:,0], name="Predicted")
            confusionMatrix = pd.crosstab(actual,predicted)
            self.saveConfusion(confusionMatrix.as_matrix(),outputdir)

            return confusionMatrix

        if self.objective == "inference":
            self.estimatedParams = self.compute()
            self.trueParams = self.paramArray[self.picks,:]
            self.saveEstimates(outputdir)
            SumSqDiff = np.sum((self.estimatedParams - self.trueParams)**2,axis=0)
            Variance = np.var(self.trueParams,axis=0)

            return np.float(SumSqDiff / Variance)

    def saveConfusion(self, confusionMatrix, outputdir):
        """
        Generate heatmap of confusion matrix showing results of cv for model comparison.
        :param confusionMatrix: confusion matrix as numpy array.
        :return: None
        """
        pdf = matplotlib.backends.backend_pdf.PdfPages(outputdir + '/cv_comparison.pdf')

        fig = plt.figure()
        plt.clf()
        ax = fig.add_subplot(111)
        ax.set_aspect(1)
        res = ax.imshow(confusionMatrix, cmap=plt.get_cmap("Purples"),
                        interpolation='nearest')

        width, height = confusionMatrix.shape

        for x in range(width):
            for y in range(height):
                ax.annotate(str(confusionMatrix[x][y]), xy=(y, x),
                            horizontalalignment='center',
                            verticalalignment='center')

        fig.colorbar(res)
        plt.xticks(range(width), self.modelNames)
        plt.yticks(range(height), self.modelNames)
        plt.title('Confusion matrix')
        pdf.savefig()
        pdf.close()

    def saveEstimates(self, outputdir):
        """
        Generate multiple plots showing results of cv for parameter inference.
        :return: None
        """
        pdf = matplotlib.backends.backend_pdf.PdfPages(outputdir + '/cv_inference.pdf')
        for i,col in enumerate(self.estimatedParams.T):
            plt.scatter(self.estimatedParams[:, i], self.trueParams[:, i], alpha=0.5)
            plt.xlabel('Estimated parameter')
            plt.ylabel('True parameter')
            low_y = np.mean( self.trueParams[:, i]) - np.std(self.trueParams[:, i]) * 2
            up_y = np.mean( self.trueParams[:, i]) + np.std(self.trueParams[:, i]) * 2
            low_x = np.mean(self.estimatedParams[:, i]) - np.std(self.estimatedParams[:, i]) * 2
            up_x = np.mean(self.estimatedParams[:, i]) + np.std(self.estimatedParams[:, i]) * 2
            Min = min(low_y,low_x)
            Max = max(up_y, up_x)
            plt.xlim(Min,Max)
            plt.ylim(Min,Max)
            plt.gca().set_aspect('equal', adjustable='box')
            pdf.savefig()
        pdf.close()



