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
        self.size = cave.Vector2(0.5, 2)  # position.x, position.y
        self.maxSlideAngle = 60  # scale.x
        self.minSlideAngle = 30  # scale.y
        self.slideForce = 5
        self.grabDistance = 0.5
        self.grabCooldown = 0.5
        self.climbingTime = 1

        self.ground = None
        self.groundChecker = None
        self.isGrounded = True
        self.isGrabbing = False
        self.isClimbing = False
        self.groundPosition = None
        self.grabPosition = None
        self.groundNormal = None
        self.verticalVelocity = 0
        self.horizontalVelocity = 0
        self.direction = 0
        self.climbingProgress = 0
        self.currentGrabCooldown = 0

        self.onGrab = []
        self.onClimb = []
        self.onGround = []
        self.onCollision = []
        self.onAir = []
        pass

    def startClimbing(self):
        if self.isClimbing or not self.isGrabbing:
            return

        self.isClimbing = True
        self.climbingProgress = 0
        for callback in self.onClimb:
            callback()

    def stopGrabbing(self):
        self.currentGrabCooldown = self.grabCooldown
        self.isGrabbing = False
        for callback in self.onAir:
            callback()

    def jump(self, strength):
        if self.isGrabbing:
            return False

        if self.isGrounded:
            self.verticalVelocity = strength
            self.ground = None
            self.groundChecker = None
            self.isGrounded = False
            self.isGrabbing = False
            self.groundPosition = None
            self.groundNormal = None
            return True
        return False

    def move(self, velocity):
        if self.isGrabbing:
            if velocity > 0 and self.direction > 0:
                self.startClimbing()
            elif velocity < 0 and self.direction < 0:
                self.startClimbing()
            else:
                self.stopGrabbing()
            return

        self.direction = 1 if velocity > 0 else -1
        if self.isGrounded:
            self.horizontalVelocity = velocity
        elif self.horizontalVelocity != 0:
            if velocity > 0:
                self.horizontalVelocity = self.horizontalVelocity if self.horizontalVelocity > 0 else -self.horizontalVelocity
            elif velocity < 0:
                self.horizontalVelocity = self.horizontalVelocity if self.horizontalVelocity < 0 else -self.horizontalVelocity
            else:
                self.horizontalVelocity = velocity
        else:
            self.horizontalVelocity = velocity
        return True

    def start(self, scene):
        transform = self.entity.getTransform()

        # We offset the origin to create a capsule-like collision system
        self.radius = self.size.x / 2
        self.height = self.size.y - self.size.x
        self.groundOriginOffset = cave.Vector3(0, self.radius, 0)
        self.topOriginOffset = cave.Vector3(0, self.radius + self.height, 0)
        self.sizeOffset = cave.Vector3(self.size.x / 2, self.size.y, 0)

        # Creates the collision checkers
        self.groundCheckers = []
        self.topCheckers = []
        self.rightCheckers = []
        self.leftCheckers = []

        iterations = 19
        angleOffset = 45
        step = (180-angleOffset*2)/(iterations-1)
        heightStep = self.height/(iterations-1)

        for i in range(iterations):
            topAngle = angleOffset + i * step
            groundAngle = 180 + topAngle
            height = i * heightStep + self.radius
            self.groundCheckers.append(MathUtils.deg2vec(groundAngle) * self.radius)
            self.topCheckers.append(MathUtils.deg2vec(topAngle) * self.radius)
            self.rightCheckers.append(cave.Vector3(self.radius, height, 0))
            self.leftCheckers.append(cave.Vector3(-self.radius, height, 0))

        # First ground update to initialize the current state
        self.updateGround(scene, transform)

    def end(self, scene):
        if self in PhysicsController.instances:
            PhysicsController.instances.remove(self)

    def update(self):
        self.delta = cave.getDeltaTime()
        transform = self.entity.getTransform()
        scene = self.entity.getScene()

        if self.isGrabbing:
            self.updateClimbing(transform)
        else:
            if self.isGrounded:
                self.updateMove(scene, transform)
                self.updateSlide(scene, transform)
            else:
                self.updateAir(scene, transform)
                self.updateGrab(scene, transform)

            if self.verticalVelocity <= 0:
                self.updateGround(scene, transform)
            else:
                self.updateTop(scene, transform)

    def updateClimbing(self, transform):
        if self.isClimbing:
            self.climbingProgress = MathUtils.clamp01(self.climbingProgress + self.delta / self.climbingTime)
            transform.position = MathUtils.lerp(self.grabStartPosition, self.grabPosition, self.climbingProgress)
            if self.climbingProgress >= 1:
                self.isClimbing = False
                self.isGrabbing = False

    def updateSlide(self, scene, transform):
        groundAngle = MathUtils.angle(self.groundNormal)
        entityAngle = 90 - (groundAngle if groundAngle <= 90 else 90 -
                            (groundAngle - 90))
        if entityAngle > self.minSlideAngle:
            directionAngleOffset = 90 if groundAngle > 90 else -90
            slideFactor = MathUtils.normalize(
                self.minSlideAngle, self.maxSlideAngle, entityAngle)
            movement = MathUtils.deg2vec(groundAngle + directionAngleOffset) * slideFactor * self.slideForce * self.delta
            if not self.checkMovementCollision(scene, transform, movement):
                transform.position += movement

    def updateGrab(self, scene, transform):
        if self.currentGrabCooldown > 0:
            self.currentGrabCooldown -= self.delta
            return

        origin = transform.position + self.topOriginOffset
        origin.y += self.radius
        target = cave.Vector3(origin.x + (self.radius * self.direction * 1.5), origin.y, origin.z)
        raycastOut = scene.rayCast(origin, target)
        if raycastOut.hit:
            topRaycastOut = scene.rayCast(raycastOut.position + cave.Vector3(self.direction * 0.1, self.grabDistance, 0),
                                          raycastOut.position + cave.Vector3(self.direction * 0.1, 0, 0))
            if topRaycastOut.hit:
                self.isGrabbing = True
                self.verticalVelocity = 0
                self.horizontalVelocity = 0
                self.climbingProgress = 0
                self.isClimbing = False
                self.grabPosition = cave.Vector3(topRaycastOut.position.x, topRaycastOut.position.y, topRaycastOut.position.z)
                self.grabStartPosition = cave.Vector3(self.grabPosition.x + ((self.radius + 0.1) * -self.direction),
                                                      self.grabPosition.y - self.size.y - self.grabDistance, topRaycastOut.position.z)
                transform.position = self.grabStartPosition
                for callback in self.onGrab:
                    callback()
        pass

    def updateAir(self, scene, transform):
        self.verticalVelocity -= PhysicsController.gravity * self.delta
        movement = cave.Vector3(self.horizontalVelocity * self.delta, self.verticalVelocity * self.delta, 0)
        transform.position.y += movement.y
        if not self.checkMovementCollision(scene, transform, movement):
            transform.position.x += movement.x

    def updateMove(self, scene, transform):
        if self.horizontalVelocity == 0:
            return

        groundAngle = MathUtils.angle(self.groundNormal)
        entityAngle = 90 - (groundAngle if groundAngle <= 90 else 90 -
                            (groundAngle - 90))
        if entityAngle >= 0 and entityAngle < self.maxSlideAngle:
            directionAngleOffset = 90 if self.horizontalVelocity < 0 else -90
            movement = MathUtils.deg2vec(groundAngle + directionAngleOffset) * MathUtils.absolute(self.horizontalVelocity) * self.delta
            if not self.checkMovementCollision(scene, transform, movement):
                transform.position += movement

        self.horizontalVelocity = 0

    def checkMovementCollision(self, scene, transform, movement):
        def check(checkers):
            for checker in checkers:
                raycastOut = scene.rayCast(transform.position + checker, transform.position + checker + movement)
                if raycastOut.hit:
                    for callback in self.onCollision:
                        callback(self.direction, raycastOut.entity, raycastOut.position, raycastOut.normal)
                    self.horizontalVelocity = 0
                    return True
            return False

        if movement.x > 0:
            return check(self.rightCheckers)
        elif movement.x < 0:
            return check(self.leftCheckers)

    def checkCollisions(self, scene, checkers, origin, minAngle, maxAngle):
        bestHitDistance = 999999
        bestCollision = None
        for checker in checkers:
            target = origin + checker
            raycastOut = scene.rayCast(origin, target + cave.Vector3(0, -0.1, 0))
            if raycastOut.hit:
                groundAngle = MathUtils.angle(raycastOut.normal)
                entityAngle = 90 - (groundAngle if groundAngle <= 90 else 90 - (groundAngle - 90))
                if entityAngle >= minAngle and entityAngle < maxAngle:
                    distance = cave.length(raycastOut.position - origin)
                    if distance < bestHitDistance:
                        bestHitDistance = distance
                        bestCollision = CollisionResult(raycastOut.entity,
                                                        cave.Vector3(raycastOut.normal.x, raycastOut.normal.y, raycastOut.normal.z),
                                                        cave.Vector3(raycastOut.position.x, raycastOut.position.y, raycastOut.position.z),
                                                        checker)
        return bestCollision

    def updateTop(self, scene, transform):
        collision = self.checkCollisions(scene, self.topCheckers, transform.position + self.topOriginOffset, -9999, 9999)
        if collision != None:
            self.verticalVelocity = 0
            transform.position = collision.position - collision.checker - self.topOriginOffset

    def updateGround(self, scene, transform):
        lastIsGrounded = self.isGrounded
        lastVelocity = self.verticalVelocity

        self.ground = None
        self.isGrounded = False
        self.groundPosition = None
        self.groundNormal = None

        collision = self.checkCollisions(scene, self.groundCheckers, transform.position + self.groundOriginOffset, 0, self.maxSlideAngle)
        if collision != None:
            self.verticalVelocity = 0
            self.ground = collision.entity
            self.groundChecker = collision.checker
            self.isGrounded = True
            self.groundPosition = collision.position
            self.groundNormal = collision.normal

        if lastIsGrounded and not self.isGrounded:
            for callback in self.onAir:
                callback()

        if self.isGrounded:
            if not lastIsGrounded:
                for callback in self.onGround:
                    callback(lastVelocity)
            transform.position = self.groundPosition - self.groundChecker - self.groundOriginOffset


class CollisionResult:
    def __init__(self, entity, normal, position, checker):
        self.entity = entity
        self.normal = normal
        self.position = position
        self.checker = checker
