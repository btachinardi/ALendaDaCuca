import cave


class GameStartSequencer(cave.Component):
    started = False

    def start(self, scene):
        GameController.onInitialized(lambda: self.initialize())

    def initialize(self):
        if GameStartSequencer.started:
            return

        GameStartSequencer.started = True
        self.game = GameController.instance
        self.game.disableCharacter()
        self.instructions = GameController.instructions
        self.instructions.hide()
        self.music = cave.playSound('Theme Music', loop=1)
        self.ui = self.entity.get('UI Element Component')
        self.loadViews()
        self.blocker = self.views['Blocker']

        self.time = 0
        self.blocking = False
        self.targetBlockerPosition = 1
        self.blockerPosition = 0
        self.position = 0
        self.targetPosition = 0

        self.slides = [
            Slide('Nostaldream Logo', 6, None, False),
            Slide('Cave Logo', 6, None, False),
            Slide('Story', 99, 'Escuro, frio... não sinto nada...\nOnde estou? Onde estava?\n\nTento encontrar um apoio,\nmas não encontro nada...'),
            Slide('Story', 99, 'Uma luz fraca aparece aos poucos,\ne com ela ouço uma leve melodia\n\nMas há algo de estranho nela,\npor algum motivo está desconexa...'),
            Slide('Story', 99, 'Aos poucos recupero meus sentidos,\nsinto cheiro de mofo, ar úmido\n\nSerá que estou em uma gruta?\n\nNão... alguém mora aqui...\nParece o lar de uma criatura...'),
            Slide('Story', 99, 'Os detalhes ao meu redor começam a retornar,\nmas não consigo me mexer e nem falar...\n\nEspera um pouco... está tudo ao contrário!\n\nSinto uma pressão ao redor do meu peito\nestou amarrada de ponta cabeça?'),
            Slide('Story', 99, 'Finalmente identifico de onde a melodia vem,\numa criatura de mais de 5 metros,\ncom cabeça de jacaré, mas que fica de pé!\n\nEla canta sua melodia enquanto mexe em seu caldeirão,\no que será que está cozinhando?'),
            Slide('Story', 99, '"E agora, o ingrediente principal..."\n\nEspera um pouco, o jacaré fala?!\n\nA criatura se aproxima de mim...\nPosso sentir seu hálito pútrido e um olhar frio...'),
            Slide('Story', 99, 'Sinto um solavanco, espera...\nO chão não está chegando cada vez mais perto?\n\nBUUUUMM\n\nSinto uma dor intensa quando a gravidade\nfaz o chão encontrar com minha cara...'),
            Slide('Story', 99, 'Mas não tenho tempo para dor, mais\numa pressão surge em meu abdomem, e de repente\nme encontro logo acima do caldeirão...\n\nPosso ver um líquido verde e borbulhante\nque começa a reagir ao tocar em meu cabelo...'),
            Slide('Story', 99, 'Fecho os olhos... será que este é o fim?'),
            Slide('Story', 99, '...'),
            Slide('Story', 99, '"Preguiçosa! Sabia que não podia confiar em você!"\n\nDe quem é esta voz? Abros os olhos lentamente...\n\nE não estou mais no caldeirão?\nOnde está aquele jacaré maldito?!'),
            Slide('Story', 99, '"Como consegue dormir em uma situação dessas?\nSó pode ser talento...\nSim! Você tem o dom de ser preguiçosa!"\n\nViro minha cabeça e vejo um menino\nvestindo uma touca vermelha e roupas esfarrapadas.'),
            Slide('Story', 99, '"Se quiser ajudar seus amigos, precisamos ser rápidos!\nO Curupira e seus capangas já estão alertas\ne procurando por você."\n\nSinto uma ventania surgindo ao nosso redor...\nNa verdade, ao redor deste menino...'),
            Slide('Story', 99, '"Talvez eu te ajude, mas provavelmente não...\nVamos ver se se você merece meu respeito primeiro.\nEstarei te esperando dentro da casa da Cuca,\nmas isso se você conseguir, é claro!"\n\nO vento aumenta, várias folhas\nse juntam e impedem minha visão...'),
            Slide('Story', 99, 'VUUUUSH'),
            Slide('Story', 99, 'Quando o vento se acalma, o menino não está mais lá,\ne me encontro sozinha em meio a esta floresta...')
        ]

        self.currentSlideIndex = 0
        self.currentSlide = self.slides[self.currentSlideIndex]
        self.currentSlideView = self.views[self.currentSlide.viewName]
        self.currentSlideView.position.setRelativeX(0)
        self.slideChanged = True

    def interact(self):
        self.nextSlide()

    def loadViews(self):
        self.views = {}
        for child in self.entity.getChildren():
            view = child.get('UI Element Component')
            self.views[child.name] = view
            view.position.setRelativeX(9999)

    def update(self):
        if not GameStartSequencer.started:
            return

        self.delta = cave.getDeltaTime()
        self.time += self.delta

        self.position = MathUtils.lerp(self.position, self.targetPosition, 0.025)
        self.ui.position.setRelativeX(self.position)

        self.blockerPosition = MathUtils.lerp(self.blockerPosition, self.targetBlockerPosition, 0.025)
        self.blocker.position.setRelativeX(self.blockerPosition)

        if self.time >= self.currentSlide.duration:
            self.nextSlide()

        if not self.slideChanged and self.blockerPosition > 0:
            if self.currentSlide.skippable:
                if self.currentSlideIndex + 1 >= len(self.slides):
                    self.instructions.showArgs('F', 'Jogar', None)
                else:
                    self.instructions.showArgs('F', 'Próximo', None)
                self.game.setInteractable(self)

            self.currentSlideView.position.setRelativeX(9999)
            self.currentSlideView = self.views[self.currentSlide.viewName]
            self.currentSlideView.position.setRelativeX(0)
            if self.currentSlide.text != None:
                self.setText(self.currentSlideView, self.currentSlide.text)
            self.slideChanged = True

    def nextSlide(self):
        self.instructions.hide()
        self.game.clearInteractable()
        self.currentSlideIndex += 1

        if self.currentSlideIndex >= len(self.slides):
            self.targetPosition = 1
            self.game.enableCharacter()
            self.music.pause()
            return

        self.time = 0
        self.currentSlide = self.slides[self.currentSlideIndex]
        self.slideChanged = False
        self.blockerPosition = -1

    def end(self, scene):
        pass

    def setText(self, view, text):
        textViews = []
        for child in view.entity.getChildren():
            ui = child.get('UI Element Component')
            if ui != None:
                textViews.append(ui)
                ui.position.setPixelY(int(9999))

        lines = text.split('\n')
        linesCount = len(lines)
        lineHeight = 50
        height = linesCount * lineHeight
        start = height / 2
        for i in range(linesCount):
            ui = textViews[i]
            ui.text = lines[i]
            ui.position.setPixelY(int(start - i * lineHeight))


class GameEndSequencer(cave.Component):
    started = False

    def start(self, scene):
        GameController.onInitialized(lambda: self.initialize())
        self.active = False

    def activate(self):
        self.active = True

    def initialize(self):
        if GameEndSequencer.started:
            return

        GameEndSequencer.started = True
        self.game = GameController.instance
        GameController.ending = self
        self.game.disableCharacter()
        self.instructions = GameController.instructions
        self.music = cave.playSound('Theme Music', loop=1)
        self.ui = self.entity.get('UI Element Component')
        self.loadViews()
        self.blocker = self.views['Blocker']

        self.active = False
        self.time = 0
        self.blocking = False
        self.targetBlockerPosition = 1
        self.blockerPosition = 0
        self.position = 1
        self.targetPosition = 0

        self.slides = [
            Slide('Story', 99, 'Esta é a casa do meu sonho...'),
            Slide('Story', 99, 'O que será que irei encontrar aqui?'),
            Slide('Story', 99, 'Obrigado por jogar\n\nA LENDA DA CUCA\n\nJogo produzido na Cave,\nengine 100% brasileira,\npara o Game Jam da Level Up'),
        ]

        self.currentSlideIndex = -1

    def interact(self):
        self.nextSlide()

    def loadViews(self):
        self.views = {}
        for child in self.entity.getChildren():
            view = child.get('UI Element Component')
            self.views[child.name] = view

    def update(self):
        if not GameEndSequencer.started or not self.active:
            return

        self.delta = cave.getDeltaTime()
        self.time += self.delta

        self.position = MathUtils.lerp(self.position, self.targetPosition, 0.025)
        self.ui.position.setRelativeX(self.position)

        self.blockerPosition = MathUtils.lerp(self.blockerPosition, self.targetBlockerPosition, 0.025)
        self.blocker.position.setRelativeX(self.blockerPosition)

        if self.time >= self.currentSlide.duration:
            self.nextSlide()

        if not self.slideChanged and self.blockerPosition > 0:
            if self.currentSlide.skippable:
                if self.currentSlideIndex + 1 >= len(self.slides):
                    self.instructions.showArgs('F', 'Sair', None)
                else:
                    self.instructions.showArgs('F', 'Próximo', None)
                self.game.setInteractable(self)

            self.currentSlideView.position.setRelativeX(9999)
            self.currentSlideView = self.views[self.currentSlide.viewName]
            self.currentSlideView.position.setRelativeX(0)
            if self.currentSlide.text != None:
                self.setText(self.currentSlideView, self.currentSlide.text)
            self.slideChanged = True

    def nextSlide(self):
        self.instructions.hide()
        self.game.clearInteractable()
        self.currentSlideIndex += 1

        if self.currentSlideIndex >= len(self.slides):
            self.targetPosition = 1
            self.game.enableCharacter()
            self.music.pause()
            cave.quitGame()
            return

        self.time = 0
        self.currentSlide = self.slides[self.currentSlideIndex]
        self.slideChanged = False
        self.blockerPosition = -1

    def end(self, scene):
        pass

    def setText(self, view, text):
        textViews = []
        for child in view.entity.getChildren():
            ui = child.get('UI Element Component')
            if ui != None:
                textViews.append(ui)
                ui.position.setPixelY(int(9999))

        lines = text.split('\n')
        linesCount = len(lines)
        lineHeight = 50
        height = linesCount * lineHeight
        start = height / 2
        for i in range(linesCount):
            ui = textViews[i]
            ui.text = lines[i]
            ui.position.setPixelY(int(start - i * lineHeight))


class Slide:
    def __init__(self, viewName, duration, text=None, skippable=True):
        self.viewName = viewName
        self.duration = duration
        self.text = text
        self.skippable = skippable
