
class ABCSummary:
    """A wrapper class over the user-defined summary func."""

    def __init__(self, summary):
        self.summary = summary

    def summarize(self, data):
        """Compute and return summary statistics from data."""

        return self.summary(data).flatten()
