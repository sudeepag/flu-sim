"""
Defines interventions in the influenza model. These include Masks, Medicines, and Vaccines.
"""
class InterventionType:
    def __init__(self):
        pass

    MASK = 0
    DOSE = 1
    VACCINE = 2


class Intervention:
    def __init__(self, type, cost):
        self.type = type
        self.cost = cost

    def __repr__(self):
        if self.type == InterventionType.MASK:
            return 'MASK'
        elif self.type == InterventionType.DOSE:
            return 'DOSE'
        elif self.type == InterventionType.VACCINE:
            return 'VACCINE'
