import cave


class InteractableController(cave.Component):
    def start(self, scene):
        self.targetZ = self.entity.getTransform()

    def update(self):
        events = cave.getEvents()

    def end(self, scene):
        pass
