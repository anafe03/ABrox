import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from sklearn.neural_network import MLPClassifier
from abrox.core.abc_utils import toArray, cross_val


class ABCNeuralNet:
    """Implements a random forest for ABC model selection."""

    def __init__(self, refTable, preprocessor):

        self._refTable = refTable
        self._pp = preprocessor

    def run(self):
        """Runs according to settings (these must be specified by user.)"""

        # Extract sum stats and model indices from ref table
        indices = toArray(self._refTable, 'idx').flatten()
        sumStat = toArray(self._refTable, 'sumstat')

        print(sumStat.shape)

        # Create a classifier
        # TODO according to user-specified settings
        # TODO 2: Implement random forest without sklearn dependency

        model = Sequential()
        model.add(Dense(1000, input_dim=sumStat.shape[1], kernel_initializer='glorot_uniform', activation='relu'))
        model.add(Dense(100, kernel_initializer='glorot_uniform', activation='relu'))
        model.add(Dense(1, kernel_initializer='glorot_uniform', activation='sigmoid'))
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam')

        # Do a 5-fold cross-validation
        # accuracies = cross_val(sumStat, indices, model, 5)
        # print("Neural net cross-val accuracies: ")
        # print(accuracies)

        # Fit on summary statistics (the more the better)
        model.fit(sumStat, indices, batch_size=64, epochs=2, shuffle=True, validation_split=0.2)

        # Predict probabilities of models on summary obs
        sumStatTest = np.array(self._pp.scaledSumStatObsData).reshape(1, -1)
        print("Probability of model 1 is: \n")
        pred = model.predict_proba(sumStatTest)

        return pred