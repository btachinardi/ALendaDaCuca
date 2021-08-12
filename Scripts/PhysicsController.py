import cave


class PhysicsController(cave.Component):
    instances = []

    def findFirstInEntity(entity):
        return next(filter(lambda i: i.entity == entity, PhysicsController.instances))

    def findFirstByName(name):
        return next(filter(lambda i: i.entity.name == name, PhysicsController.instances))

    def findFirstByTag(tag):
        return next(filter(lambda i: i.entity.hasTag(tag), PhysicsController.instances))

    def findInEntity(entity):
        return filter(lambda i: i.entity == entity, PhysicsController.instances)

    def findByName(name):
        return filter(lambda i: i.entity.name == name, PhysicsController.instances)

    def findByTag(tag):
        return filter(lambda i: i.entity.hasTag(tag), PhysicsController.instances)

    gravity = 30

    def __init__(self):
        PhysicsController.instances.append(self)
        # Configurations
        self.size = cave.Vector2(1, 2)
        self.maxSlideAngle = 60
        self.minSlideAngle = 30
        self.slideForce = 5

        self.ground = None
        self.groundChecker = None
        self.isGrounded = True
        self.groundPosition = None
        self.groundAttriction = 0
        self.groundNormal = None
        self.verticalVelocity = 0
        self.direction = 0
        self.onGround = []
        self.onAir = []
        pass

    def jump(self, strength):
        if self.isGrounded:
            self.verticalVelocity = strength
            self.ground = None
            self.groundChecker = None
            self.isGrounded = False
            self.groundPosition = None
            self.groundAttriction = 0
            self.groundNormal = None
            return True
        return False

    def move(self, direction):
        if self.isGrounded:
            self.direction = direction
            return True
        return False

    def start(self, scene):
        transform = self.entity.getTransform()

        # We offset the origin to create a capsule-like collision system
        self.radius = self.size.x / 2
        self.originOffset = cave.Vector3(0, self.radius, 0)

        # Creates the ground collision checkers
        self.groundCheckers = []
        iterations = 19
        angleOffset = 30
        step = (180-angleOffset*2)/(iterations-1)
        for i in range(iterations):
            angle = 180 + angleOffset + i * step
            self.groundCheckers.append(MathUtils.deg2vec(angle) * self.radius)

        # First ground update to initialize the current state
        self.updateGround(scene, transform)

    def end(self, scene):
        if self in PhysicsController.instances:
            PhysicsController.instances.remove(self)

    def update(self):
        self.delta = cave.getDeltaTime()
        transform = self.entity.getTransform()
        scene = self.entity.getScene()

        if self.isGrounded:
            self.updateMove(transform)
            self.updateSlide(transform)
        else:
            self.updateAir(transform)

        self.updateGround(scene, transform)
        pass

    def updateSlide(self, transform):
        groundAngle = MathUtils.angle(self.groundNormal)
        entityAngle = 90 - (groundAngle if groundAngle <= 90 else 90 -
                            (groundAngle - 90))
        if entityAngle > self.minSlideAngle:
            directionAngleOffset = 90 if groundAngle > 90 else -90
            slideFactor = MathUtils.normalize(
                self.minSlideAngle, self.maxSlideAngle, entityAngle)
            transform.position += MathUtils.deg2vec(
                groundAngle + directionAngleOffset) * slideFactor * self.slideForce * self.delta

    def updateAir(self, transform):
        self.verticalVelocity -= PhysicsController.gravity * self.delta
        transform.position.y += self.verticalVelocity * self.delta
        transform.position.x += self.direction * self.delta

    def updateMove(self, transform):
        if self.direction == 0:
            return
        groundAngle = MathUtils.angle(self.groundNormal)
        entityAngle = 90 - (groundAngle if groundAngle <= 90 else 90 -
                            (groundAngle - 90))
        if entityAngle >= 0 and entityAngle < self.maxSlideAngle:
            directionAngleOffset = 90 if self.direction < 0 else -90
            transform.position += MathUtils.deg2vec(
                groundAngle + directionAngleOffset) * MathUtils.absolute(self.direction) * self.delta

        self.direction = 0

    def updateGround(self, scene, transform):
        lastIsGrounded = self.isGrounded
        lastVelocity = self.verticalVelocity
        origin = transform.position + self.originOffset
        self.ground = None
        self.isGrounded = False
        self.groundPosition = None
        self.groundAttriction = 0
        self.groundNormal = None

        bestHitDistance = 999999
        for checker in self.groundCheckers:
            target = origin + checker
            raycastOut = scene.rayCast(origin, target + cave.Vector3(0, -0.1, 0))
            if raycastOut.hit:
                groundAngle = MathUtils.angle(raycastOut.normal)
                entityAngle = 90 - (groundAngle if groundAngle <= 90 else 90 -
                                    (groundAngle - 90))
                if entityAngle >= 0 and entityAngle < self.maxSlideAngle:
                    self.verticalVelocity = 0
                    distance = cave.length(raycastOut.position - origin)
                    if distance < bestHitDistance:
                        bestHitDistance = distance
                        self.ground = raycastOut.entity
                        self.groundChecker = checker
                        self.isGrounded = True
                        self.groundPosition = cave.Vector3(
                            raycastOut.position.x, raycastOut.position.y, raycastOut.position.z)
                        self.groundAttriction = 0.5
                        self.groundNormal = cave.Vector3(
                            raycastOut.normal.x, raycastOut.normal.y, raycastOut.normal.z)

        if lastIsGrounded and not self.isGrounded:
            for callback in self.onAir:
                callback()

        if self.isGrounded:
            if not lastIsGrounded:
                for callback in self.onGround:
                    callback(lastVelocity)
            targetPosition = self.groundPosition - \
                self.groundChecker - self.originOffset
            if cave.length(transform.position - targetPosition) > 0.1:
                transform.position = self.groundPosition - \
                    self.groundChecker - self.originOffset
