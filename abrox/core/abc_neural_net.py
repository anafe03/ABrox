import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from abrox.core.abc_utils import toArray, cross_val
from keras.layers.core import Lambda
from keras import backend as K
from sklearn import preprocessing


class ABCNeuralNet:
    """Implements a random forest for ABC model selection."""

    def __init__(self, refTable, preprocessor, objective):

        self._refTable = refTable
        self._pp = preprocessor
        self.objective = objective

    def run(self,rawData,model):
        """Runs according to settings (these must be specified by user.)"""

        if self.objective == 'comparison':

            # Extract sum stats and model indices from ref table
            indices = toArray(self._refTable, 'idx').flatten()
            sumStat = toArray(self._refTable, 'sumstat')

            print(sumStat.shape)

            # Create a classifier
            # TODO according to user-specified settings
            # TODO 2: Implement random forest without sklearn dependency

            model = Sequential()
            model.add(Dense(10, input_dim=sumStat.shape[1], kernel_initializer='glorot_uniform', activation='relu'))
            model.add(Dense(10, kernel_initializer='glorot_uniform', activation='relu'))
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

        else:

            X = toArray(self._refTable, 'sumstat')
            y = toArray(self._refTable, 'param')

            print(X.shape)
            print(y.shape)

            X_val = X[:5000]
            X_train = X[5000:]

            y_val = y[:5000]
            y_train = y[5000:]

            print('Normalizing...')
            scaler = preprocessing.StandardScaler().fit(X_train)

            X_train = scaler.transform(X_train)
            X_val = scaler.transform(X_val)

            features = X.shape[1]
            outputs = y.shape[1]
            print("Running model on {} features".format(features))
            print("Prediction {} parameters".format(outputs))

            load = True
            if load:
                wkrt = 1 # nonesense

            else:

                model = Sequential()
                model.add(Dense(features, input_shape=(features,), activation='relu'))
                model.add(Lambda(lambda x: K.dropout(x, level=0.1)))
                model.add(Dense(features, activation='relu'))
                model.add(Lambda(lambda x: K.dropout(x, level=0.1)))
                model.add(Dense(features, activation='relu'))
                model.add(Lambda(lambda x: K.dropout(x, level=0.1)))
                model.add(Dense(y.shape[1], activation='linear'))

                # Compile model
                model.compile(loss='mean_squared_error', optimizer='adam')

                # Fit model
                history = model.fit(x=X_train, y=y_train,
                                    batch_size=32,
                                    epochs=20,
                                    shuffle=True,
                                    validation_data=(X_val,y_val),
                                    verbose=True)

                # Save model
                model.save('/Users/ulf.mertens/Desktop/nndl/my_model.h5')

                print("Finished fitting")

            sumStatTest = np.array(self._pp.scaledSumStatObsData).reshape(1, -1)
            sumStatTest = scaler.transform(sumStatTest)

            print('Prediction with dropout...')

            N = 100
            posteriorSamples = np.empty(shape=(N,outputs))
            for i in range(N):
                posteriorSamples[i,] = model.predict(sumStatTest)

            print('Finished predicting...')

            loss = None #history.history['loss']
            val_loss = None  #history.history['val_loss']

            return rawData, loss, val_loss, posteriorSamples



# convModel = models.Sequential()
# convModel.add(layers.Conv1D(32,160,strides=12,activation='relu',input_shape=(48,1)))
# convModel.add(layers.MaxPooling1D(pool_size=2))
# convModel.add(layers.Conv1D(32,40,strides=8,activation='relu'))
# convModel.add(layers.MaxPooling1D(pool_size=2))
# convModel.add(layers.Conv1D(64,80,strides=2,activation='relu'))
# convModel.add(layers.MaxPooling1D(pool_size=2))
# convModel.add(layers.Flatten())
# convModel.add(layers.Dense(64,activation='relu'))
# convModel.add(layers.Dense(2,activation='linear'))