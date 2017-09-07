class Model:
    def __init__(self,
                 name="",
                 priors=None,
                 simulate=None,
                 summary=None,
                 distance_metric=None,
                 distance=None):

        self.name = name
        self.prior = priors
        self.simulate = simulate
        self.summary = summary
        self.distance_metric = distance_metric
        self.distance = distance
