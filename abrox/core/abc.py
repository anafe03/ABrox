from abrox.core.error_check import ErrorCheck
from abrox.core.preparation import Prepare


class Abc:

    def __init__(self,config):
        self.config = config
        self.modelList = None
        self.modelNames = None
        self.metaInfo = None
        self.obsData = None

    def errorCheck(self):
        return ErrorCheck(self.config)

    def prepare(self):
        """
        Get necessary data from configuration dict.
        :return: None
        """
        prepare = Prepare(self.config)
        self.modelList, self.modelNames = prepare.buildModel()
        # simulations, keep, objective, nModels, paramNames = prepare.getMetaInfo()
        self.metaInfo = prepare.getMetaInfo()
        self.obsData = prepare.getObservedData(self.modelList)

    def preprocess(self):
        """
        Preprocess run.
        :return:
        """
        pass

    def reject(self):
        pass

    def report(self):
        pass

    def run(self):
        # error checking
        # preparation
        # preprocessing
        # rejecting
        # reporting
        pass