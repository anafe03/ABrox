
class AbcSummary:

    def __init__(self, summary):
        self.summary = summary

    def summarize(self,simData):
        """Compute and return summary statistics."""

        return self.summary(simData)
