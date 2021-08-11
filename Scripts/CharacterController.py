import cave


class CharacterController(cave.Component):
    instances = []

    def findFirstInEntity(entity):
        return next(filter(lambda i: i.entity == entity, CharacterController.instances))

    def findFirstByName(name):
        return next(filter(lambda i: i.entity.name == name, CharacterController.instances))

    def findFirstByTag(tag):
        return next(filter(lambda i: i.entity.hasTag(tag), CharacterController.instances))

    def findInEntity(entity):
        return filter(lambda i: i.entity == entity, CharacterController.instances)

    def findByName(name):
        return filter(lambda i: i.entity.name == name, CharacterController.instances)

    def findByTag(tag):
        return filter(lambda i: i.entity.hasTag(tag), CharacterController.instances)

    def __init__(self):
        CharacterController.instances.append(self)
        self.speed = 5
        self.runSpeed = 10
        self.maxStamina = 10
        self.staminaReset = self.maxStamina * 0.75
        self.currentStamina = self.maxStamina
        self.staminaRecoveryRate = 0.5
        self.staminaRunRate = 1.5
        self.staminaCoooldown = False
        self.jumpStrength = 10
        self.rotateSmooth = 0.2
        self.isFirstUpdate = True
        self.direction = 0
        self.targetDirection = self.direction
        self.delta = 0

    def jump(self):
        self.physics.jump(self.jumpStrength)

    def run(self, direction):
        if self.staminaCoooldown:
            self.walk(direction)
            return

        self.targetDirection = 180 if direction > 0 else 0
        self.physics.move(direction * self.runSpeed)
        self.currentStamina -= self.staminaRunRate * self.delta
        if self.currentStamina <= 0:
            self.currentStamina = 0
            self.staminaCoooldown = True

    def walk(self, direction):
        self.targetDirection = 180 if direction > 0 else 0
        self.physics.move(direction * self.speed)

    def start(self, scene):
        children = self.entity.getChildren()
        for child in children:
            if child.hasTag('Camera Look Target'):
                self.cameraLookTarget = child.getTransform()
            if child.hasTag('Camera Pos Offset'):
                self.cameraPosOffset = child.getTransform()

    def end(self, scene):
        if self in CharacterController.instances:
            CharacterController.instances.remove(self)

    def firstUpdate(self):
        self.physics = PhysicsController.findFirstInEntity(self.entity)

    def update(self):
        if self.isFirstUpdate:
            self.isFirstUpdate = False
            self.firstUpdate()
        transform = self.entity.getTransform()

        self.delta = cave.getDeltaTime()
        self.currentStamina = MathUtils.clamp(
            0, self.maxStamina, self.currentStamina + self.staminaRecoveryRate * self.delta)

        if self.currentStamina > self.staminaReset:
            self.staminaCoooldown = False

        self.direction = MathUtils.lerp(
            self.direction, self.targetDirection, self.rotateSmooth)
        transform.lookAt(MathUtils.deg2vecXZ(self.direction))
