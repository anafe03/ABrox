import numpy as np
from keras.models import Sequential, Model
from keras import layers
from keras import Input
from abrox.core.abc_utils import toArray, heteroscedastic_loss
from keras import backend as K
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from keras.models import load_model
from keras.utils import plot_model


from abrox.core.abc_concrete_dropout import ConcreteDropout


class ABCNeuralNet:
    """Implements a random forest for ABC model selection."""

    def __init__(self, refTable, preprocessor, settings):

        self._refTable = refTable
        self._pp = preprocessor
        self._nnSettings = settings['specs']
        self.outputdir = settings['outputdir']
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.dropout = None
        self.wd = None
        self.dd = None

    def constructTrainAndValSet(self):
        """
        Construct training and validation set.
        :return: None
        """
        X = toArray(self._refTable, 'sumstat')
        y = toArray(self._refTable, 'param')
        self.X_train, self.X_val, self.y_train, self.y_val = \
            train_test_split(X, y, test_size=self._nnSettings['val_size'])

    def normalize(self):
        """
        Normalize features.
        :return: fitted scaler
        """
        scaler = preprocessing.StandardScaler().fit(self.X_train)
        scaler.transform(self.X_train,copy=False)
        scaler.transform(self.X_val,copy=False)
        return scaler

    def setConcreteDropout(self):
        """
        Choose hyperparameters for Concrete Dropout.
        :return:
        """
        l = 1e-4
        self.wd = l ** 2. / (self.X_train.shape[0])
        self.dd = 2. / (self.X_train.shape[0])

    def add_layers(self, size, prev_tensor):
        """
        Add dense layer with concrete dropout.
        :param size: number of nodes in hidden layer
        :param prev_tensor: the previous tensor
        :return: the final layer
        """
        return ConcreteDropout(
            layers.Dense(size, activation=self._nnSettings['activation']),
            weight_regularizer=self.wd, dropout_regularizer=self.dd)(prev_tensor)

    def build_keras_model(self):
        """
        Build a simple Keras model.
        :return: the model
        """
        features = self.X_train.shape[1]
        outputs = self.y_train.shape[1]
        input_tensor = Input(shape=(features, ))
        x = input_tensor

        for i in range(self._nnSettings['hidden_layers']):
            units = int(self._nnSettings['hidden_layer_sizes'][i] * features)
            x = self.add_layers(units, x)

        mean = ConcreteDropout(layers.Dense(outputs),
                               weight_regularizer=self.wd,
                               dropout_regularizer=self.dd)(x)
        log_var = ConcreteDropout(layers.Dense(outputs),
                                  weight_regularizer=self.wd,
                                  dropout_regularizer=self.dd)(x)

        output_tensor = layers.merge([mean, log_var], mode='concat')

        return Model(input_tensor, output_tensor)

    def storeDropoutRates(self, model):
        """
        Return the optimized dropout probabilities.
        :param model: the keras model
        :return: the probabilities
        """
        dropoutProbs = []
        for i in range(self._nnSettings['hidden_layers'] -1):
            dropoutProbs.append(K.eval(K.exp(model.layers[i].weights[2])))
        self.dropout = dropoutProbs

    def makePredictions(self, model, scaler, outputs, N=500):
        """
        Predict at observed data using Dropout at test-time.
        :param model: keras model
        :param scaler: the scaler used to scale training set
        :param outputs: number of output units (times 2)
        :param N: predictions
        :return: the samples from the posterior predictive.
        """

        sumStatTest = np.array(self._pp.scaledSumStatObsData).reshape(1, -1)
        sumStatTest = scaler.transform(sumStatTest)

        posteriorSamples = np.empty(shape=(N, outputs*2))
        for i in range(N):
            posteriorSamples[i,] = model.predict(sumStatTest)

        means = np.mean(posteriorSamples,axis=0)
        vars = np.var(posteriorSamples,axis=0)

        mean1 = means[0]
        mean2 = means[1]
        epi1 = vars[0] # model uncertainty
        epi2 = vars[1] # model uncertainty
        alea1 = np.exp(means[2]) # data uncertainty
        alea2 = np.exp(means[3]) # data uncertainty
        return mean1, mean2, epi1, epi2, alea1, alea2

    def run(self,rawData):
        """
        Run the whole procedure and return the predictions with uncertainty.
        :param rawData:
        :return:
        """

        self.constructTrainAndValSet()

        features = self.X_train.shape[1]
        outputs = self.y_train.shape[1]

        print("Training size: ", self.X_train.shape[0])
        print("Validation size: ", self.X_val.shape[0])
        print("Running model on {} features".format(features))
        print("Predicting {} parameters".format(outputs))

        self.setConcreteDropout()

        scaler = self.normalize()

        if self._nnSettings['load_model'] is not None:
            print("Loading pretrained model...")
            model = load_model(self.outputdir + self._nnSettings['load_model'])
        else:
            model = self.build_keras_model()


        #plot_model(model, to_file=self.outputdir + 'model.png')
        # model.summary()

        model.compile(loss=heteroscedastic_loss, optimizer=self._nnSettings['optimizer'])

        # Fit model
        history = model.fit(x=self.X_train,
                            y=self.y_train,
                            batch_size=32,
                            epochs=self._nnSettings['epochs'],
                            validation_data=(self.X_val,self.y_val),
                            verbose=False)

        # Save model
        if self._nnSettings['load_model'] is None:
            model.save(self.outputdir + 'keras_model.h5')

        # self.storeDropoutRates(model)

        relevantOutputs = self.makePredictions(model,scaler,outputs)

        loss = history.history['loss']
        val_loss = history.history['val_loss']

        return rawData, loss, val_loss, relevantOutputs