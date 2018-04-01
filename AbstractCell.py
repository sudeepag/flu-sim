class AbstractCell:
    def __init__(self, attributes, state):
        self.attributes = attributes
        self.state = state

    def update(self, updates):
        pass

    def intervene(self, intervention):
        pass
