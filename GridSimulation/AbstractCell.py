class AbstractCell:
    def __init__(self, attributes, state):
        self.attributes = attributes
        self.state = state

    def update(self, histogram):
        pass

    def intervene(self, intervention):
        pass
