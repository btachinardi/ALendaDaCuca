import cave


class InstructionTriggerController(cave.Component):
    def start(self, scene):
        GameController.onInitialized(lambda: self.initialize())

    def initialize(self):
        self.instructions = GameController.instructions

    def update(self):
        Utils.updateTrigger(self)

    def end(self, scene):
        pass

    def onExitTrigger(self):
        self.instructions.hide()

    def onEnterTrigger(self):
        config = self.data['instructions']
        self.instructions.show(config)



