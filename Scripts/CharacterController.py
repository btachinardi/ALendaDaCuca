import cave


class CharacterController(cave.Component):
    instances = []

    def findFirstInEntity(entity):
        return next(filter(lambda i: i.entity == entity, CharacterController.instances))

    def findFirstByName(name):
        return next(filter(lambda i: i.entity.name == name, CharacterController.instances))

    def findFirstByTag(tag):
        return next(filter(lambda i: i.entity.hasTag(tag), CharacterController.instances))

    def findInEntity(entity):
        return filter(lambda i: i.entity == entity, CharacterController.instances)

    def findByName(name):
        return filter(lambda i: i.entity.name == name, CharacterController.instances)

    def findByTag(tag):
        return filter(lambda i: i.entity.hasTag(tag), CharacterController.instances)

    def __init__(self):
        CharacterController.instances.append(self)
        self.speed = 3
        self.runSpeed = 5
        self.maxStamina = 10
        self.staminaReset = self.maxStamina * 0.75
        self.currentStamina = self.maxStamina
        self.staminaRecoveryRate = 0.5
        self.staminaRunRate = 1.5
        self.staminaCoooldown = False
        self.jumpStrength = 10
        self.rotateSmooth = 0.2
        self.isFirstUpdate = True
        self.direction = 0
        self.targetDirection = self.direction
        self.delta = 0

    def jump(self):
        if self.physics.jump(self.jumpStrength):
            self.stateMachine.setState(CharacterSM.Jumping)

    def run(self, direction):
        if self.staminaCoooldown:
            self.walk(direction)
            return

        self.targetDirection = 180 if direction > 0 else 0
        if self.physics.move(direction * self.runSpeed):
            self.stateMachine.setState(CharacterSM.Running)
            self.currentStamina -= self.staminaRunRate * self.delta
            if self.currentStamina <= 0:
                self.currentStamina = 0
                self.staminaCoooldown = True

    def walk(self, direction):
        self.targetDirection = 180 if direction > 0 else 0
        if self.physics.move(direction * self.speed):
            self.stateMachine.setState(CharacterSM.Walking)

    def start(self, scene):
        children = self.entity.getChildren()
        for child in children:
            if child.hasTag('Camera Look Target'):
                self.cameraLookTarget = child.getTransform()
            if child.hasTag('Camera Pos Offset'):
                self.cameraPosOffset = child.getTransform()
            if child.hasTag('View'):
                self.view = child

        self.stateMachine = CharacterSM(self.view.get(
            'Mesh Component'),
            {
            CharacterSM.Idle:  'LauraIdle',
            CharacterSM.InAir:  'LauraJumpAir',
            CharacterSM.Jumping:  'LauraJumpStart',
            CharacterSM.Landing:  'LauraJumpFallStop',
            CharacterSM.RunLanding:  'LauraJumpFallRun',
            CharacterSM.HardLanding:  'LauraFallHard',
            CharacterSM.Sliding:  'LauraSlide',
            CharacterSM.Walking:  'LauraWalking',
            CharacterSM.Running:  'LauraRunning',
        })

    def end(self, scene):
        if self in CharacterController.instances:
            CharacterController.instances.remove(self)

    def firstUpdate(self):
        self.physics = PhysicsController.findFirstInEntity(self.entity)
        self.physics.onGround.append(lambda v: self.onGround(v))
        self.physics.onAir.append(lambda: self.onAir())
        if self.physics.isGrounded:
            self.stateMachine.setState(CharacterSM.Idle)
        else:
            self.stateMachine.setState(CharacterSM.InAir)

    def onGround(self, velocity):
        print('ground')
        if velocity < -10:
            self.stateMachine.setState(CharacterSM.HardLanding)
        elif velocity < -5:
            self.stateMachine.setState(CharacterSM.Landing)
        else:
            self.stateMachine.setState(CharacterSM.Idle)

    def onAir(self):
        print('air')
        self.stateMachine.setState(CharacterSM.InAir)

    def update(self):
        if self.isFirstUpdate:
            self.isFirstUpdate = False
            self.firstUpdate()
        transform = self.entity.getTransform()

        self.delta = cave.getDeltaTime()
        self.currentStamina = MathUtils.clamp(
            0, self.maxStamina, self.currentStamina + self.staminaRecoveryRate * self.delta)

        if self.currentStamina > self.staminaReset:
            self.staminaCoooldown = False

        self.direction = MathUtils.lerp(
            self.direction, self.targetDirection, self.rotateSmooth)
        transform.lookAt(MathUtils.deg2vecXZ(self.direction))
        self.stateMachine.update(self.delta)


class State:
    def __init__(self, name, contextMesh=None, animation=None):
        self.name = name
        self.animation = animation
        self.contextMesh = contextMesh
        self.transitions = []
        self.time = 0

    def update(self, delta):
        self.time += delta
        for transition in self.transitions:
            result = transition.update()
            if result != None:
                return result
        return self.name

    def reset(self):
        self.time = 0

    def enter(self):
        self.time = 0
        for transition in self.transitions:
            transition.enter()
        if self.animation != None and self.contextMesh != None:
            self.contextMesh.setAnimation(self.animation)

    def exit(self):
        for transition in self.transitions:
            transition.exit()

    def addTransition(self, checker, priority=0):
        self.transitions.append(StateTransition(checker, priority))
        self.transitions.sort(reverse=True, key=lambda t: t.priority)

    def addAnimationTransition(self, targetState, priority=-999):
        def transitionChecker():
            return targetState if self.contextMesh.getAnimationLoops() > 0 else None
        self.transitions.append(StateTransition(transitionChecker, priority))

    def addTimeTransition(self, time, targetState, priority=0):
        def transitionChecker():
            return targetState if self.time > time else None
        self.transitions.append(StateTransition(transitionChecker, priority))

    def setAnimation(self, animation):
        self.animation = animation


class StateTransition:
    def __init__(self, checker, state, priority=0):
        self.checker = checker
        self.priority = priority

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        return self.checker()


class StateMachine:
    def __init__(self, contextMesh=None):
        self.states = {}
        self.currentState = None
        self.defaultState = None
        self.contextMesh = contextMesh
        pass

    def addState(self, name, animation=None):
        if self.defaultState == None:
            self.defaultState = name

        state = State(name, self.contextMesh)
        self.states[name] = state
        if animation != None:
            state.setAnimation(animation)
        return state

    def addAnimationState(self, state, animationsMap):
        animation = animationsMap[state] if animationsMap != None else state
        return self.addState(state, animation)

    def update(self, delta):
        newState = self.defaultState
        if self.currentState != None:
            state = self.states[self.currentState]
            newState = state.update(delta)

        # Setting state causes it to reset, so we can´t call it from update if it hasn't changed
        if self.currentState != newState:
            self.setState(newState)

    def setState(self, newState):
        if self.currentState != newState:
            if self.currentState != None:
                self.states[self.currentState].exit()
            self.currentState = newState
            if self.currentState != None:
                self.states[self.currentState].enter()
        else:
            if self.currentState != None:
                self.states[self.currentState].reset()


class CharacterSM(StateMachine):
    Idle = 'Idle'
    InAir = 'Air'
    Jumping = 'Jumping'
    Landing = 'Landing'
    HardLanding = 'HardLanding'
    RunLanding = 'RunLanding'
    Sliding = 'Sliding'
    Walking = 'Walking'
    Running = 'Running'

    def __init__(self, contextMesh=None, animationsMap=None):
        super().__init__(contextMesh)

        self.idle = self.addAnimationState(CharacterSM.Idle, animationsMap)
        self.inAir = self.addAnimationState(CharacterSM.InAir, animationsMap)
        self.jumping = self.addAnimationState(CharacterSM.Jumping, animationsMap)
        self.landing = self.addAnimationState(CharacterSM.Landing, animationsMap)
        self.runLanding = self.addAnimationState(CharacterSM.RunLanding, animationsMap)
        self.hardLanding = self.addAnimationState(CharacterSM.HardLanding, animationsMap)
        self.sliding = self.addAnimationState(CharacterSM.Sliding, animationsMap)
        self.walking = self.addAnimationState(CharacterSM.Walking, animationsMap)
        self.running = self.addAnimationState(CharacterSM.Running, animationsMap)

        self.walking.addTimeTransition(0.1, CharacterSM.Idle)
        self.running.addTimeTransition(0.1, CharacterSM.Idle)
        self.jumping.addAnimationTransition(CharacterSM.InAir)
        self.landing.addAnimationTransition(CharacterSM.Idle)
        self.hardLanding.addAnimationTransition(CharacterSM.Idle)
        self.runLanding.addAnimationTransition(CharacterSM.Idle)
