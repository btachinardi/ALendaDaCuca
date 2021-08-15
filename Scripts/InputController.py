import cave


class InputController(cave.Component):
    instances = []

    def __init__(self):
        print('Input Controller Initialized')
        InputController.instances.append(self)
        self.up = KeyInput(['W', 'UP'])
        self.down = KeyInput(['S', 'DOWN'])
        self.left = KeyInput(['A', 'LEFT'])
        self.right = KeyInput(['D', 'RIGHT'])
        self.jump = KeyInput(['SPACE'])
        self.interact = KeyInput(['F'])
        self.shift = KeyInput(['LSHIFT'])

        self.allInputs = [self.up, self.down, self.left,
                          self.right, self.jump, self.interact, self.shift]
        pass

    def start(self, scene):
        pass

    def end(self, scene):
        pass

    def update(self):
        events = cave.getEvents()
        for input in self.allInputs:
            for key in input.keyBindings:
                if events.pressed(key):
                    input.start = True
                    input.active = True
                    input.end = False
                    for pressAction in input.onPress:
                        pressAction()
                    break
                if events.active(key):
                    input.start = False
                    input.active = True
                    input.end = False
                    break
                if events.released(key):
                    input.start = False
                    input.active = False
                    input.end = True
                    break
        pass


class KeyInput:
    def __init__(self, keyBindings):
        self.keyBindings = keyBindings
        self.start = False
        self.active = False
        self.end = False
        self.onPress = []
        pass

