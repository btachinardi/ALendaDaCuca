import cave


class PhysicsController(cave.Component):
    instances = []
    gravity = 9.81

    def __init__(self):
        PhysicsController.instances.append(self)
        # Configurations
        self.speed = 1
        self.jumpStrength = 1
        self.size = cave.Vector2(1, 2)

        # Physics data
        self.velocity = cave.Vector3(0, 0, 0)
        self.mass = 1
        self.grounded = False
        self.groundedPosOffset = cave.Vector3(0, 0.1, 0)

        # Bounds data
        self.topLeftOffset = cave.Vector3(self.size.x / -2, self.size.y, 0)
        self.topRightOffset = cave.Vector3(self.size.x / 2, self.size.y, 0)
        self.bottomLeftOffset = cave.Vector3(self.size.x / -2, 0, 0)
        self.bottomRightOffset = cave.Vector3(self.size.x / 2, 0, 0)

        # Collision data
        self.collisionEntity = None
        self.collisionPosition = None
        self.collisionNormal = None
        pass

    def addForce(self, force):
        self.velocity += force

    def start(self, scene):
        pass

    def end(self, scene):
        pass

    def update(self):
        self.delta = cave.getDeltaTime()
        transform = self.entity.getTransform()
        scene = self.entity.getScene()

        self.velocity.y -= self.delta * PhysicsController.gravity
        self.calculateCollisions(scene, transform)

        transform.position += self.velocity * self.delta
        pass

    def calculateCollisions(self, scene, transform):
        if self.velocity.y > 0:
            if (self.velocity.x > 0):
                if self.calculateCollision(scene, transform, self.bottomRightOffset):
                    return
            elif (self.velocity.x < 0):
                if self.calculateCollision(scene, transform, self.bottomLeftOffset):
                    return
            if self.calculateCollision(scene, transform, self.topRightOffset):
                return
            if self.calculateCollision(scene, transform, self.topLeftOffset):
                return
        elif self.velocity.y < 0:
            if (self.velocity.x > 0):
                if self.calculateCollision(scene, transform, self.topRightOffset):
                    return
            elif (self.velocity.x < 0):
                if self.calculateCollision(scene, transform, self.topLeftOffset):
                    return
            if self.calculateCollision(scene, transform, self.bottomRightOffset):
                return
            if self.calculateCollision(scene, transform, self.bottomLeftOffset):
                return

        self.grounded = False
        pass

    def calculateCollision(self, scene, transform, offset):
        origin = transform.position + offset
        target = origin + self.velocity * self.delta
        raycastOut = scene.rayCast(origin, target)
        if raycastOut.hit:
            self.collisionEntity = raycastOut.entity
            self.collisionPosition = raycastOut.position
            self.collisionNormal = raycastOut.normal
            self.velocity *= 0
            transform.position = self.collisionPosition - offset
            self.grounded = True
            return True
        return False
