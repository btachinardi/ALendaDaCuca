class Utils:

    def printProperties(target):
        objectProps = [propName for propName in dir(
            target) if not callable(getattr(target, propName))]
        print('\nProperties for ' + type(target).__name__ + ': ' +
              ''.join([str(item) + ', ' for item in objectProps]))

    def printMethods(target):
        objectMethods = [methodName for methodName in dir(
            target) if callable(getattr(target, methodName))]
        print('\nMethods for ' + type(target).__name__ + ': ' +
              ''.join([str(item) + ', ' for item in objectMethods]))

    def printAll(target):
        Utils.printProperties(target)
        Utils.printMethods(target)

    def globalPosition(entity, parentTransformList):
        position = entity.getTransform().position
        for parent in reversed(parentTransformList):
            position += parent.position
        return position

    def processData(entity, parents=[]):
        result = {}
        children = entity.getChildren()

        if len(children) == 0:
            return Utils.globalPosition(entity, parents) if 'waypoint' in entity.name.lower() else \
                (entity if 'collider' in entity.name.lower() else entity.name)

        for child in children:
            splitName = child.name.split('=')
            if len(splitName) == 1:
                result[splitName[0].strip()] = Utils.processData(child, parents + [entity.getTransform()])
            elif len(splitName) == 2:
                value = splitName[1].strip()
                result[splitName[0].strip()] = Utils.floatTryParse(value)

        return result

    waypoints = None

    def getWaypoints(scene, name):
        if Utils.waypoints == None:
            Utils.loadWaypoints(scene)
        return Utils.waypoints[name]

    def loadWaypoints(scene):
        waypointsContainer = scene.getEntity('Waypoints')
        Utils.waypoints = {}
        for child in waypointsContainer.getChildren():
            Utils.waypoints[child.name] = Utils.getWaypointsInChild(child)

    def getWaypointsInChild(entity):
        parentPos = entity.getTransform().position
        list = []
        for child in entity.getChildren():
            position = parentPos + child.getTransform().position
            list.append(position)

        return list

    def updateTrigger(target):
        if not hasattr(target, 'data'):
            target.currentTarget = None
            target.data = Utils.processData(target.entity)
            return

        newTarget = None

        if not hasattr(target, 'rect'):
            transform = target.entity.getTransform()
            pos = transform.position
            scale = transform.scale * 2
            if 'collider' in target.data:
                collider = target.data['collider']
                colTransform = collider.getTransform()
                pos = cave.Vector3(colTransform.position.x + pos.x, colTransform.position.y + pos.y, 0)
                scale = cave.Vector3(colTransform.scale.x * scale.x, colTransform.scale.y * scale.y, 0)
                collider.getScene().remove(collider)

            target.rect = Rect(pos.x - scale.x / 2, pos.y - scale.y / 2, scale.x, scale.y)

        for physics in PhysicsController.instances:
            isValid = False
            for tag in target.data['tags']:
                if physics.entity.hasTag(tag):
                    isValid = True
                    break
            if not isValid:
                continue

            targetTransform = physics.entity.getTransform()
            targetPos = targetTransform.position
            targetScale = targetTransform.scale
            targetRect = Rect(targetPos.x - targetScale.x / 2, targetPos.y, targetScale.x, targetScale.y)
            if target.rect.checkForCollision(targetRect):
                newTarget = physics
                break

        if newTarget != target.currentTarget:
            target.currentTarget = newTarget
            if target.currentTarget == None:
                target.onExitTrigger()
            else:
                target.onEnterTrigger()

    def floatTryParse(value):
        try:
            return float(value)
        except ValueError:
            return value

    def intTryParse(value):
        try:
            return int(value)
        except ValueError:
            return value


class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def checkForCollision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < self.radius + other.radius


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def checkForCollision(self, other):
        return self.x < other.x + other.width and \
            self.x + self.width > other.x and \
            self.y < other.y + other.height and \
            self.y + self.height > other.y
