class Model(object):
    def __dict__(self):
        """
        This method converts the document model attributes to a dictionary for upsertion into MongoDB
        """
        raise NotImplementedError()
