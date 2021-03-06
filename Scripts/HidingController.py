import cave


class HidingController(cave.Component):
    def start(self, scene):
        self.firstUpdate = True

    def update(self):
        if self.firstUpdate:
            self.firstUpdate = False
            self.player = CharacterController.instances[0]
            self.instructions = InstructionsController.instances[0]
            self.camera = CameraController.instances[0]
            self.game = GameController.instances[0]
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
