import cave


class Game(cave.Component):
    def __init__(self):
        print('Game Initialized')
        self.isFirstUpdate = True
        pass

    def start(self, scene):
        print('Start')
        pass

    def end(self, scene):
        pass

    def firstUpdate(self):
        self.input = InputController.instances[0]
        self.character = CharacterController.instances[0]
        pass

    def update(self):
        if self.isFirstUpdate:
            self.isFirstUpdate = False
            self.firstUpdate()

        if self.input.jump.start:
            self.character.jump()
        if self.input.left.active:
            self.character.walk(-1)
        if self.input.right.active:
            self.character.walk(1)
        pass
