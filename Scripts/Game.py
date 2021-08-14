import cave


class Game(cave.Component):
    def __init__(self):
        print('Game Initialized')
        self.isFirstUpdate = True
        pass

    def start(self, scene):
        pass

    def end(self, scene):
        pass

    def firstUpdate(self):
        self.input = InputController.instances[0]
        self.character = CharacterController.instances[0]
        self.camera = CameraController.instances[0]
        self.instructions = InstructionsController.instances[0]
        self.camera.setTarget(self.character.entity.getTransform(
        ), self.character.cameraLookTarget, self.character.cameraPosOffset)

    def update(self):
        if self.isFirstUpdate:
            self.isFirstUpdate = False
            self.firstUpdate()

        if self.input.left.active:
            if self.input.shift.active:
                self.character.run(-1)
            else:
                self.character.walk(-1)
        if self.input.right.active:
            if self.input.shift.active:
                self.character.run(1)
            else:
                self.character.walk(1)
        if self.input.jump.start:
            if self.instructions.isVisible:
                self.instructions.hide()
            else:
                self.instructions.show('A', 'Correr', 'Shift')
            self.character.jump()
