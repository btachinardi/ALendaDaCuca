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
        self.hardFallSpeed = -20
        self.softFallSpeed = -12.5
        self.speed = 3
        self.runSpeed = 5
        self.hidingSpeed = 5
        self.maxStamina = 10
        self.staminaReset = self.maxStamina * 0.75
        self.currentStamina = self.maxStamina
        self.staminaRecoveryRate = 0.5
        self.staminaRunRate = 1.5
        self.staminaCoooldown = False
        self.jumpStrength = 10
        self.isFirstUpdate = True
        self.direction = 0
        self.targetDirection = self.direction
        self.delta = 0

    def allowInput(self):
        return self.stateMachine.currentState != CharacterSM.HardLanding and \
            self.stateMachine.currentState != CharacterSM.SoftLanding and \
            self.stateMachine.currentState != CharacterSM.Climbing and \
            self.stateMachine.currentState != CharacterSM.Dead and \
            self.stateMachine.currentState != CharacterSM.Dying and \
            self.stateMachine.currentState != CharacterSM.Hiding and \
            self.stateMachine.currentState != CharacterSM.Hidden and \
            self.stateMachine.currentState != CharacterSM.Tripping

    def climb(self):
        if self.physics.climb():
            self.stateMachine.setState(CharacterSM.Climbing)

    def jump(self):
        if not self.allowInput():
            return

        if self.physics.isGrabbing:
            self.physics.stopGrabbing()
            return

        if self.physics.jump(self.jumpStrength):
            self.stateMachine.setState(CharacterSM.Jumping, 0.1)

    def hide(self, waypoints):
        def hideEnd():
            self.stateMachine.setState(CharacterSM.Hidden)
            self.physics.enabled = False
        self.physics.animateSpeed(waypoints, self.hidingSpeed, hideEnd)
        self.stateMachine.setState(CharacterSM.Hiding)

    def run(self, direction):
        if not self.allowInput():
            return

        if self.staminaCoooldown:
            self.walk(direction)
            return

        self.targetDirection = 180 if direction > 0 else 0
        if self.physics.move(direction * self.runSpeed):
            self.stateMachine.setState(CharacterSM.Running, 0.1)
            self.currentStamina -= self.staminaRunRate * self.delta
            if self.currentStamina <= 0:
                self.currentStamina = 0
                self.staminaCoooldown = True

    def walk(self, direction):
        if not self.allowInput():
            return

        self.targetDirection = 180 if direction > 0 else 0
        if self.physics.move(direction * self.speed):
            self.stateMachine.setState(CharacterSM.Walking, 0.1)

    def start(self, scene):
        children = self.entity.getChildren()
        for child in children:
            if child.hasTag('Camera Look Target'):
                self.cameraLookTarget = child.getTransform()
            if child.hasTag('Camera Pos Offset'):
                self.cameraPosOffset = child.getTransform()
            if child.hasTag('View'):
                self.view = child

        self.viewMesh = self.view.get('Mesh Component')
        self.stateMachine = CharacterSM(self.viewMesh, self.getAnimationMap())

    def getAnimationMap(self):
        return {
            CharacterSM.Idle:  'LauraIdle',
            CharacterSM.InAir:  'LauraJumpAir',
            CharacterSM.Jumping:  'LauraJumpStart',
            CharacterSM.SoftLanding:  'LauraJumpFallStop',
            CharacterSM.RunLanding:  'LauraJumpFallRun',
            CharacterSM.HardLanding:  'LauraFallHard',
            CharacterSM.Sliding:  'LauraSlide',
            CharacterSM.Walking:  'LauraWalking',
            CharacterSM.Running:  'LauraRunning',
            CharacterSM.Grabbing:  'LauraGrabbing',
            CharacterSM.Climbing:  'LauraClimbing',
            CharacterSM.Pushing:  'LauraPushing',
            CharacterSM.Tripping:  'LauraTripping',
            CharacterSM.Dying:  'LauraDeathForward',
            CharacterSM.Dead:  'LauraDead',
            CharacterSM.Hiding:  'LauraStealthWalk',
            CharacterSM.Hidden:  'LauraCrouch',
        }

    def end(self, scene):
        if self in CharacterController.instances:
            CharacterController.instances.remove(self)

    def firstUpdate(self):
        self.physics = PhysicsController.findFirstInEntity(self.entity)
        self.physics.onGround.append(lambda v, e: self.onGround(v, e))
        self.physics.onAir.append(lambda: self.onAir())
        self.physics.onGrab.append(lambda: self.onGrab())
        self.physics.onClimb.append(lambda: self.onClimb())
        self.physics.onTrip.append(lambda: self.onTrip())
        self.physics.onCollision.append(lambda d, e, p, n: self.onCollision(d, e, p, n))
        if self.physics.isGrounded:
            self.stateMachine.setState(CharacterSM.Idle)
        else:
            self.stateMachine.setState(CharacterSM.InAir)

    def onTrip(self):
        self.stateMachine.setState(CharacterSM.Tripping)

    def onCollision(self, direction, entity, position, normal):
        rigidBody = entity.get('Rigid Body Component')
        self.stateMachine.setState(CharacterSM.Pushing)
        if rigidBody != None:
            rigidBody.applyImpulse(direction * 0.5, 0, 0, position)

    def onGrab(self):
        self.stateMachine.setState(CharacterSM.Grabbing)

    def onClimb(self):
        self.stateMachine.setState(CharacterSM.Climbing)

    def onGround(self, velocity, entity):
        if entity.hasTag('Death'):
            self.stateMachine.setState(CharacterSM.Dying)
            return

        if velocity < self.hardFallSpeed:
            self.stateMachine.setState(CharacterSM.HardLanding)
        elif velocity < self.softFallSpeed:
            self.stateMachine.setState(CharacterSM.SoftLanding)
        else:
            self.stateMachine.setState(CharacterSM.Idle)

    def onAir(self):
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

        self.stateMachine.update(self.delta)


class State:
    def __init__(self, name, contextMesh=None, animation=None):
        self.name = name
        self.animation = animation
        self.contextMesh = contextMesh
        self.transitions = []
        self.transitionsAllowed = []
        self.time = 0

    def update(self, delta):
        self.time += delta
        for transition in self.transitions:
            result = transition.update()
            if result != None:
                return {'newState': result, 'blendTime': transition.blendTime}
        return None

    def reset(self):
        self.time = 0

    def enter(self, blendTime):
        self.time = 0
        for transition in self.transitions:
            transition.enter()
        if self.animation != None and self.contextMesh != None:
            self.contextMesh.setAnimation(self.animation, blendTime)

    def exit(self):
        for transition in self.transitions:
            transition.exit()

    def addTransition(self, checker, blendTime=0.25, priority=0):
        self.transitions.append(StateTransition(checker, blendTime, priority))
        self.transitions.sort(reverse=True, key=lambda t: t.priority)

    def addAnimationTransition(self, targetState, time=0.9, blendTime=0.25, priority=-999):
        def transitionChecker():
            return targetState if self.contextMesh.getAnimationProgress() > time else None
        self.transitions.append(StateTransition(transitionChecker, blendTime, priority))

    def onlyTransitionTo(self, targetStates):
        for state in targetStates:
            self.transitionsAllowed.append(state)

    def canTransitionTo(self, targetState):
        if len(self.transitionsAllowed) == 0:
            return True
        if targetState in self.transitionsAllowed:
            return True
        return False

    def addTimeTransition(self, time, targetState, blendTime=0.25, priority=0):
        def transitionChecker():
            return targetState if self.time > time else None
        self.transitions.append(StateTransition(transitionChecker, blendTime, priority))

    def setAnimation(self, animation):
        self.animation = animation


class StateTransition:
    def __init__(self, checker, blendTime, priority=0):
        self.checker = checker
        self.priority = priority
        self.blendTime = blendTime

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
        result = None
        if self.currentState != None:
            state = self.states[self.currentState]
            result = state.update(delta)

        # Setting state causes it to reset, so we can´t call it from update if it hasn't changed
        if result != None and self.currentState != result['newState']:
            self.setState(result['newState'], result['blendTime'])

    def setState(self, newState, blendTime=0.25):
        if self.currentState != newState:
            currentState = self.states[self.currentState] if self.currentState != None else None
            canTransition = currentState == None or currentState.canTransitionTo(newState)
            if canTransition:
                if self.currentState != None:
                    self.states[self.currentState].exit()
                self.currentState = newState
                if self.currentState != None:
                    self.states[self.currentState].enter(blendTime)
        else:
            if self.currentState != None:
                self.states[self.currentState].reset()


class CharacterSM(StateMachine):
    Idle = 'Idle'
    InAir = 'Air'
    Jumping = 'Jumping'
    SoftLanding = 'Landing'
    HardLanding = 'HardLanding'
    RunLanding = 'RunLanding'
    Sliding = 'Sliding'
    Walking = 'Walking'
    Running = 'Running'
    Grabbing = 'Grabbing'
    Climbing = 'Climbing'
    Pushing = 'Pushing'
    Tripping = 'Tripping'
    Dead = 'Dead'
    Dying = 'Dying'
    Hiding = 'Hiding'
    Hidden = 'Hidden'

    def __init__(self, contextMesh=None, animationsMap=None):
        super().__init__(contextMesh)

        self.idle = self.addAnimationState(CharacterSM.Idle, animationsMap)
        self.inAir = self.addAnimationState(CharacterSM.InAir, animationsMap)
        self.jumping = self.addAnimationState(CharacterSM.Jumping, animationsMap)
        self.landing = self.addAnimationState(CharacterSM.SoftLanding, animationsMap)
        self.runLanding = self.addAnimationState(CharacterSM.RunLanding, animationsMap)
        self.hardLanding = self.addAnimationState(CharacterSM.HardLanding, animationsMap)
        self.sliding = self.addAnimationState(CharacterSM.Sliding, animationsMap)
        self.walking = self.addAnimationState(CharacterSM.Walking, animationsMap)
        self.running = self.addAnimationState(CharacterSM.Running, animationsMap)
        self.grabbing = self.addAnimationState(CharacterSM.Grabbing, animationsMap)
        self.climbing = self.addAnimationState(CharacterSM.Climbing, animationsMap)
        self.pushing = self.addAnimationState(CharacterSM.Pushing, animationsMap)
        self.tripping = self.addAnimationState(CharacterSM.Tripping, animationsMap)
        self.dead = self.addAnimationState(CharacterSM.Dead, animationsMap)
        self.dying = self.addAnimationState(CharacterSM.Dying, animationsMap)
        self.hiding = self.addAnimationState(CharacterSM.Hiding, animationsMap)
        self.hidden = self.addAnimationState(CharacterSM.Hidden, animationsMap)

        self.walking.addTimeTransition(0.1, CharacterSM.Idle)
        self.running.addTimeTransition(0.1, CharacterSM.Idle)
        self.pushing.addTimeTransition(0.1, CharacterSM.Idle)
        self.jumping.addAnimationTransition(CharacterSM.InAir)
        self.landing.addAnimationTransition(CharacterSM.Idle)
        self.hardLanding.addAnimationTransition(CharacterSM.Idle)
        self.runLanding.addAnimationTransition(CharacterSM.Idle)
        self.climbing.addAnimationTransition(CharacterSM.Idle)
        self.tripping.addAnimationTransition(CharacterSM.Idle)
        self.dying.addAnimationTransition(CharacterSM.Dead)

        self.dead.onlyTransitionTo([None])
        self.dying.onlyTransitionTo([CharacterSM.Dead])
        self.pushing.onlyTransitionTo([CharacterSM.Idle, CharacterSM.Dying])
        self.inAir.onlyTransitionTo([CharacterSM.Idle, CharacterSM.HardLanding, CharacterSM.SoftLanding, CharacterSM.RunLanding, CharacterSM.Grabbing, CharacterSM.Dying])
        self.jumping.onlyTransitionTo([CharacterSM.InAir, CharacterSM.Idle, CharacterSM.HardLanding, CharacterSM.SoftLanding, CharacterSM.RunLanding, CharacterSM.Grabbing, CharacterSM.Dying])
