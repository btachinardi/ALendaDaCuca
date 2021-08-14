import cave


class CameraTriggerController(cave.Component):
    def start(self, scene):
        pass

    def update(self):
        self.camera = CameraController.instances[0]
        Utils.updateTrigger(self)

    def end(self, scene):
        pass

    def onExitTrigger(self):
        self.camera.exitZone()

    def onEnterTrigger(self):
        config = self.data['camera']
        self.camera.enterZone(config['distance'], config['angle'], config['offset'], config['look'])
