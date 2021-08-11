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
