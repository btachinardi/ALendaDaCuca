import cave


class GameController(cave.Component):
    instance = None
    input = None
    player = None
    camera = None
    instructions = None
    ending = None
    onInitializedCallback = []
    isInitialized = False

    def onInitialized(callback):
        if GameController.isInitialized:
            callback()
        else:
            GameController.onInitializedCallback.append(callback)

    def setInteractable(self, target):
        self.currentInteractable = target

    def clearInteractable(self):
        self.currentInteractable = None

    def enableCharacter(self):
        self.characterEnabled = True

    def disableCharacter(self):
        self.characterEnabled = False

    def end(self, scene):
        pass

    def start(self, scene):
        print('Start')
        self.currentInteractable = None

    def firstUpdate(self):
        self.characterEnabled = False
        scene = self.entity.getScene()
        GameController.instance = self
        GameController.input = scene.getEntity('Input').get('InputController')
        GameController.player = scene.getEntity('Player Character').get('CharacterController')
        GameController.camera = scene.getEntity('Camera').get('CameraController')
        GameController.instructions = scene.getEntity('Instructions').get('InstructionsController')
        GameController.camera.setTarget(GameController.player.entity.getTransform(), GameController.player.cameraLookTarget, GameController.player.cameraPosOffset)
        GameController.isInitialized = True
        for callback in GameController.onInitializedCallback:
            callback()

    def update(self):

        if self.characterEnabled:
            if self.input.left.active:
                if self.input.shift.active:
                    self.player.run(-1)
                else:
                    self.player.walk(-1)
            if self.input.right.active:
                if self.input.shift.active:
                    self.player.run(1)
                else:
                    self.player.walk(1)

            if self.input.jump.start:
                self.player.jump()

        if self.input.interact.start:
            if self.currentInteractable != None:
                self.currentInteractable.interact()
