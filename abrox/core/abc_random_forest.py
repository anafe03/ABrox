import numpy as np
from sklearn.ensemble import RandomForestClassifier
from abrox.core.abc_utils import toArray


class ABCRandomForest:
    """Implements a random forest for ABC model selection."""

    def __init__(self, refTable, preprocessor, settings, modelNames):

        self._refTable = refTable
        self._pp = preprocessor
        self._settings = settings
        self._modelNames = modelNames

    def run(self):
        """Runs according to settings (these must be specified by user.)"""

        rf = RandomForestClassifier(**self._settings['specs'])

        # Extract sum stats and model indices from ref table
        indices = toArray(self._refTable, 'idx').flatten()
        sumStat = toArray(self._refTable, 'sumstat')

        # Do a 5-fold cross-validation
        accuracies = self._cross_val(sumStat, indices, rf, 5)

        # Fit on summary statistics (the more the better)
        rf.fit(sumStat, indices)

        # Predict probabilities of models on summary obs
        sumStatTest = np.array(self._pp.scaledSumStatObsData).reshape(1, -1)
        pred = rf.predict_proba(sumStatTest)

        return {mod : np.round(pred[0,i],3) for i, mod in enumerate(self._modelNames)}

    def _cross_val(self, X, y, classifier, nfolds=10):
        """
        Implements a custom cross-validation. The parameter
        nfolds controls the split of the data.
        """

        # Make sure dimensions agree
        assert X.shape[0] == y.shape[0], "Number of observations should equal" \
                                         "number of labels."

        # Concatenate data in order to shuffle without changing X-y correspondence
        data = np.c_[X, y]

        # Shuffle data (swaps rows when 2D - works OK for us)
        np.random.seed(42)
        np.random.shuffle(data)

        # Split data into (almost) equal folds (returns a list of arrays)
        # and we cast the list into a numpy array in order to do list indexing
        data = np.array(np.array_split(data, nfolds))

        # Do the k-fold cross-validation
        accs = []
        for k in range(nfolds):
            # Get current test set
            X_k_test = data[k][:, :-1]
            y_k_test = data[k][:, -1]

            # Get remaining indices and current training set
            remaining_idx = [i for i, v in enumerate(data) if i != k]
            X_k_train = np.vstack(data[remaining_idx])[:, :-1]
            y_k_train = np.vstack(data[remaining_idx])[:, -1]

            # Fit and predict with classifier
            classifier.fit(X_k_train, y_k_train)
            yhat = classifier.predict(X_k_test)

            # Store error rate
            accs.append(self._accuracy(y_k_test, yhat))

        return np.array(accs)

    def _accuracy(self, y, yhat):
        """A utility function to compute the accuracy of the classifier"""

        return np.sum(y == yhat) / len(y)
