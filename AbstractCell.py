"""
Abstract class to define the interface for a cell in any CA implementation.
Holds attribute and state, but allows the implementing class to define them.
"""

class AbstractCell:
    def __init__(self, attributes, state):
        self.attributes = attributes
        self.state = state

    def update(self, histogram):
        pass

    def intervene(self, intervention):
        pass
