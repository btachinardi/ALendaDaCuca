import cave


class CharacterController(cave.Component):
    instances = []

    def __init__(self):
        CharacterController.instances.append(self)
        self.speed = 1
        self.jumpStrength = 10
        self.isFirstUpdate = True
        pass

    def jump(self):
        if self.physics.grounded:
            self.physics.addForce(cave.Vector2(0, self.jumpStrength))
        pass

    def walk(self, direction):
        print(self.physics.grounded)
        if self.physics.grounded:
            self.physics.addForce(cave.Vector2(direction * self.speed, 0))
        pass

    def start(self, scene):
        pass

    def firstUpdate(self):
        self.physics = PhysicsController.instances[0]
        pass

    def update(self):
        if self.isFirstUpdate:
            self.isFirstUpdate = False
            self.firstUpdate()
        pass
