import cave


class InstructionTriggerController(cave.Component):
    def start(self, scene):
        pass

    def update(self):
        self.instructions = InstructionsController.instances[0]
        Utils.updateTrigger(self)

    def end(self, scene):
        pass

    def onExitTrigger(self):
        self.instructions.hide()

    def onEnterTrigger(self):
        config = self.data['instructions']
        self.instructions.show(config)



