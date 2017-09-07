
class statsModelHandler:
    """statsModelHandler class."""

    def __init__(self, stats_model):
        self.sm = stats_model
        self.fit = stats_model.fit()

    def predict(self, param):
        return self.sm.predict(param).flatten()

    def refit(self, y):
        return self.sm.__class__(y, self.sm.data.exog).fit()
