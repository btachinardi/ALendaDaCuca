import cave


class CameraController(cave.Component):
    instances = []

    def __init__(self):
        CameraController.instances.append(self)
        self.angle = 30
        self.distance = 10
        self.target = None
        self.smoothPosition = 0.1
        self.smoothRotation = 0.05
        self.lookAtVector = cave.Vector3(0, 0, 1)

    def setTarget(self, target, lookTarget, positionOffset):
        self.target = target
        self.lookTarget = lookTarget
        self.positionOffset = positionOffset

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
