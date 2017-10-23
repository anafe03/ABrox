
class Summary:
    """Summary class"""

    def __init__(self, summary):
        self.summary = summary

    def summarize(self,simData):
        """ Compute summary statistics"""
        return self.summary(simData)
