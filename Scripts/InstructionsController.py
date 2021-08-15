import cave


class InstructionsController(cave.Component):

    def start(self, scene):
        self.isVisible = False
        self.isAnimating = False
        self.keyText = None
        self.modifierText = None
        self.instructionText = None
        self.targetPosition = 0
        self.verticalPosition = 0
        self.showPosition = 75
        self.hidePosition = 0
        self.transform = self.entity.get('UI Element Component')
        self.transform.position.setPixelY(int(self.hidePosition))
        self.verticalPosition = self.hidePosition
        self.targetPosition = self.verticalPosition
        children = self.entity.getChildren()
        for child in children:
            if child.name == 'Plus Sign':
                self.plusSign = child.get('UI Element Component')
            if child.name == 'Keyboard Key Single':
                self.singleKey = child.get('UI Element Component')
            if child.name == 'Keyboard Key Long':
                self.longKey = child.get('UI Element Component')
            if child.name == 'Instruction Text':
                self.instruction = child.get('UI Element Component')

    def show(self, config):
        self.showArgs(config['key'], config['text'], config['modifier'])

    def showArgs(self, keyText, instructionText, modifierText):

        if modifierText == 'None' or modifierText == 'none':
            modifierText = None

        self.isVisible = True
        self.targetPosition = self.showPosition
        self.isAnimating = True
        self.keyText = keyText
        self.modifierText = modifierText
        self.instructionText = instructionText
        self.instruction.text = ':' + instructionText
        self.singleKey.text = keyText

        if modifierText != None:
            self.plusSign.position.setPixelY(75)
            self.longKey.position.setPixelY(75)
            self.longKey.text = modifierText
        else:
            self.plusSign.position.setPixelY(0)
            self.longKey.position.setPixelY(0)

    def hide(self):
        self.isVisible = False
        self.targetPosition = self.hidePosition
        self.isAnimating = True

    def update(self):
        if self.isAnimating:
            self.verticalPosition = MathUtils.lerp(self.verticalPosition, self.targetPosition, 0.2)
            self.transform.position.setPixelY(int(self.verticalPosition))
            if MathUtils.absolute(self.verticalPosition - self.targetPosition) <= 1:
                self.isAnimating = False

    def end(self, scene):
        pass


