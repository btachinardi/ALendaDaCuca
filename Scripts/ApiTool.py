import cave
import caveui as ui


class ApiTool(ui.DebugTab):
    def __init__(self):
        super().__init__()
        cList = dir(cave)

        self._classes = []
        self._functions = []
        self._variables = []

        for obj in cList:
            if obj.startswith("_"):
                continue

            attr = getattr(cave, obj)
            if isinstance(attr, type):
                self._classes.append(obj)
            else:
                if callable(attr):
                    self._functions.append(obj)
                else:
                    self._variables.append(obj)

    def _showVar(self, name, attr, prefix="cave."):
        tName = type(attr).__name__
        ui.text(prefix + name)

    def _showFunc(self, name, attr, prefix="cave."):
        params = []
        ui.text(prefix + name + "(...)")

    def draw(self):
        ui.text("Here is a list of all the cave global variables and functions:")
        ui.text("(Note: See Docs for the full description)")
        ui.separator()

        if len(self._variables) > 0:
            if ui.treeNodeStart("Global Variables"):
                for var in self._variables:
                    attr = getattr(cave, var)
                    self._showVar(var, attr)
                ui.treeNodeEnd()

        if len(self._functions) > 0:
            if ui.treeNodeStart("Global Functions"):
                for func in self._functions:
                    attr = getattr(cave, func)
                    self._showFunc(func, attr)
                ui.treeNodeEnd()

            ui.separator()
            ui.text("Here is a list of all the cave classes:")
            ui.text("(Note: See Docs for the full description)")

            for obj in self._classes:
                if ui.header("cave." + obj):
                    attr = getattr(cave, obj)
                    functions = []
                    variables = []
                    for a in dir(attr):
                        if a.startswith("_"):
                            continue

                        a2 = getattr(attr, a)
                        if callable(a2):
                            functions.append(a)
                        else:
                            variables.append(a)

                    if len(variables) > 0:
                        if ui.treeNodeStart("Attributes##"+obj):
                            for var in variables:
                                self._showVar(var, getattr(attr, var), "self.")
                            ui.treeNodeEnd()

                    if len(functions) > 0:
                        if ui.treeNodeStart("Methods##"+obj):
                            for func in functions:
                                self._showFunc(
                                    func, getattr(attr, func), "self.")
                            ui.treeNodeEnd()









