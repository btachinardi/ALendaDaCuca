import cave


class HidingController(cave.Component):

    def start(self, scene):
        GameController.onInitialized(lambda: self.initialize())

    def initialize(self):
        self.player = GameController.player
        self.instructions = GameController.instructions
        self.camera = GameController.camera
        self.game = GameController.instance

    def update(self):
        Utils.updateTrigger(self)

    def end(self, scene):
        pass

    def onExitTrigger(self):
        self.instructions.hide()
        self.game.clearInteractable()

    def onEnterTrigger(self):
        config = self.data['instructions']
        self.instructions.show(config)
        self.game.setInteractable(self)

    def interact(self):
        if self.player.stateMachine.currentState == CharacterSM.Hiding:
            return

        if self.player.stateMachine.currentState == CharacterSM.Hidden:
            pass
        else:
            transform = self.player.entity.getTransform()
            bestDistance = 9999
            bestWaypoints = None
            for dict in self.data['waypoints'].values():
                waypoints = list(dict.values())
                distance = cave.length(waypoints[0] - transform.position)
                if distance < bestDistance:
                    bestDistance = distance
                    bestWaypoints = waypoints

            pos = transform.position
            currentPosition = cave.Vector3(pos.x, pos.y, pos.z)
            self.waypoints = [currentPosition] + bestWaypoints
            self.player.hide(bestWaypoints)
            self.camera.enterZone(self.data['camera'])


