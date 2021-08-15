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


class GameEndTriggerController(cave.Component):
    def start(self, scene):
        GameController.onInitialized(lambda: self.initialize())

    def initialize(self):
        self.instructions = GameController.instructions
        self.game = GameController.instance
        self.camera = GameController.camera

    def update(self):
        Utils.updateTrigger(self)

    def end(self, scene):
        pass

    def interact(self):
        GameController.ending.activate()

    def onExitTrigger(self):
        self.instructions.hide()
        self.game.clearInteractable()
        self.camera.exitZone()

    def onEnterTrigger(self):
        config = self.data['instructions']
        self.instructions.show(config)
        self.game.setInteractable(self)
        config = self.data['camera']
        self.camera.enterZone(config)
