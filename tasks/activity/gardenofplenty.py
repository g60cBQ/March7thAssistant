from .doubleactivity import DoubleActivity


class GardenOfPlenty(DoubleActivity):
    def __init__(self, name, enabled, instance_type):
        super().__init__(name, enabled,instance_type)
        self.instance_type = instance_type