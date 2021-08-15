import cave


class GameStartSequencer(cave.Component):
    started = False

    def start(self, scene):
        if GameStartSequencer.started:
            return

        GameStartSequencer.started = True
        cave.playSound('Theme Music')
        self.loadViews()
        self.blocker = self.views['Blocker']

        self.time = 0
        self.blocking = False
        self.targetBlockerPosition = 1
        self.blockerPosition = 0

        self.slides = [
            Slide('Nostaldream Logo', 6),
            Slide('Cave Logo', 6),
            Slide('Story 1', 15, 'Escuro, frio... não sinto nada...\nOnde estou? Onde estava?\nTento encontrar um apoio, mas\nnão encontro nada...'),
            Slide('Story 2', 15),
            Slide('Story 3', 15),
            Slide('Story 4', 15),
            Slide('Story 5', 15),
        ]

        self.currentSlideIndex = 0
        self.currentSlide = self.slides[self.currentSlideIndex]
        self.currentSlideView = self.views[self.currentSlide.viewName]
        self.currentSlideView.position.setRelativeX(0)
        self.slideChanged = True

    def loadViews(self):
        self.views = {}
        for child in self.entity.getChildren():
            view = child.get('UI Element Component')
            self.views[child.name] = view
            view.position.setRelativeX(9999)

    def update(self):
        self.delta = cave.getDeltaTime()
        self.time += self.delta

        self.blockerPosition = MathUtils.lerp(self.blockerPosition, self.targetBlockerPosition, 0.05)
        self.blocker.position.setRelativeX(self.blockerPosition)

        if self.time >= self.currentSlide.duration:
            self.currentSlideIndex += 1
            self.time = 0
            self.currentSlide = self.slides[self.currentSlideIndex]
            self.slideChanged = False
            self.blockerPosition = -1

        if not self.slideChanged and self.blockerPosition > 0:
            self.currentSlideView.position.setRelativeX(9999)
            self.currentSlideView = self.views[self.currentSlide.viewName]
            self.currentSlideView.position.setRelativeX(0)
            self.slideChanged = True

    def end(self, scene):
        pass


class Slide:
    def __init__(self, viewName, duration):
        self.viewName = viewName
        self.duration = duration
