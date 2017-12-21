import pandas as pd
import matplotlib.pyplot as plt


class Plotter:

    def __init__(self, samples, paramNames):
        self.samples = samples
        self.paramNames = paramNames

    def toPandas(self):
        """
        Convert numpy array to pandas dataframe
        :return: dataframe
        """
        return pd.DataFrame(self.samples,columns=self.paramNames)

    def plot(self):
        df = self.toPandas()

        for column in df:
            plt.hist(df[column])
            plt.title("Posterior")
            plt.xlabel(column)
            plt.ylabel("Frequency")

        plt.show()

