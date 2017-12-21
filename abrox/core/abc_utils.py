import numpy as np
import pandas as pd
import pickle

# ABC utility functions


# Euclidean distance
def euclideanDistance(a, b, axis=1):
    """
    Compute euclidean distance either for each row (default)
    or for a and b being one-element arrays (axis=0)
    :param a: Simulated summary statistics
    :param b: observed summary statistics
    :param axis: row (1) or col(0)
    :return: euclidean distance
    """
    return np.linalg.norm(a-b, axis=axis)


# convert pandas object column to np.array
def toArray(df, name):
    """
    Convert pandas column to numpy array.
    :param df: the pandas DataFrame
    :param name: the column name
    :return: a multidimensional numpy array
    """
    alist = list(df[name].values)
    if isinstance(alist[0], (list, np.ndarray)):
        return np.array(alist)
    else:
        return np.array(alist).reshape(-1, 1)


def cross_val(X, y, classifier, nfolds=5):
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
        accs.append(accuracy(y_k_test, yhat))

    return np.array(accs)


def accuracy(y, yhat):
    """A utility function to compute the accuracy of the classifier"""

    return np.sum(y == yhat) / len(y)


def read_external(path):
    """
    Read external reference table as csv and convert to ABrox ref table.
    :param path: path to file
    :return: reference table as pandas dataframe.
    """
    dfRaw = pd.read_csv(path,sep=",")

    paramCols = [col for col in dfRaw if col.startswith('p')]
    sumstatCols = [col for col in dfRaw if col.startswith('s')]

    refTable = pd.DataFrame(index=dfRaw.index,columns=['idx','param','sumstat'])
    refTable['idx'] = dfRaw['idx']
    refTable['param'] = dfRaw[paramCols].as_matrix().tolist()

    sumstatArray = dfRaw[sumstatCols].as_matrix().tolist()
    sumstats = [np.array(sumstatList) for sumstatList in sumstatArray]
    refTable['sumstat'] = sumstats

    refTable['distance'] = dfRaw['distance']

    return refTable


def pickle_results(output, outputdir):
    """Pickles the output file and fail gently if not successful."""

    with open(outputdir + '/_results.p', 'wb+') as outfile:
        pickle.dump(output, outfile, pickle.HIGHEST_PROTOCOL)
