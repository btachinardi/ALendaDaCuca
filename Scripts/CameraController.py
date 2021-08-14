import cave


class CameraController(cave.Component):
    instances = []

    def __init__(self):
        CameraController.instances.append(self)
        self.angle = 30
        self.originalAngle = self.angle
        self.distance = 5
        self.originalDistance = self.distance
        self.target = None
        self.smoothPosition = 0.1
        self.smoothRotation = 0.05
        self.lookAtVector = cave.Vector3(0, 0, 1)

    def setTarget(self, target, lookTarget, positionOffset):
        self.target = target
        self.lookTarget = lookTarget
        self.positionOffset = positionOffset
        self.originalOffsetX = positionOffset.position.x
        self.originalLookX = lookTarget.position.x

    def enterZone(self, config):
        self.enterZoneArgs(config['distance'], config['angle'], config['offset'], config['look'])

    def enterZoneArgs(self, distance, angle, positionX, lookX):
        self.positionOffset.position.x = positionX
        self.lookTarget.position.x = lookX
        self.distance = distance
        self.angle = angle

    def exitZone(self):
        self.positionOffset.position.x = self.originalOffsetX
        self.lookTarget.position.x = self.originalLookX
        self.distance = self.originalDistance
        self.angle = self.originalAngle

    def start(self, scene):
        pass

    def update(self):
        if self.target == None:
            return

        transform = self.entity.getTransform()

        # Sets the distance based on the angle and distance configured
        globalPosition = self.target.transformVector(
            self.positionOffset.position)
        targetPosition = globalPosition + \
            MathUtils.deg2vecYZ(self.angle) * self.distance
        transform.position = MathUtils.lerp(
            transform.position, targetPosition, self.smoothPosition)

        # Sets the rotation to aim at the target object
        globalLookAt = self.target.transformVector(
            self.lookTarget.position)
        targetLookAt = globalLookAt - transform.position
        self.lookAtVector = MathUtils.lerp(
            self.lookAtVector, targetLookAt, self.smoothRotation)
        transform.lookAt(self.lookAtVector, cave.Vector3(0, 1, 0))

    def end(self, scene):
        pass
