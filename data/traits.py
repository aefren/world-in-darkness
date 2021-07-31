from language import *


class Trait:
    name = str()
    exclude = []

    def __init__(self):
        self.exclude = []

    def __str__(self):
        return self.name


class Brave(Trait):
    name = "brave"

    def __init__(self):
        super().__init__()
        self.exclude = [Craven]


class Arbitrary(Trait):
    name = "arbitrary"

    def __init__(self):
        super().__init__()
        self.exclude = [Just]


class Arrogant(Trait):
    name = "arrogant"

    def __init__(self):
        super().__init__()
        self.exclude = [Humble]



class Chaste(Trait):
    name = "chaste"

    def __init__(self):
        super().__init__()
        self.exclude = [Lustful]


class Craven(Trait):
    name = "craven"

    def __init__(self):
        super().__init__()
        self.exclude = [Brave]


class Curious(Trait):
    name = "curious"


class Deceitful(Trait):
    name = "deceitful"

    def __init__(self):
        super().__init__()
        self.exclude=[Honest]


class Diligent(Trait):
    name = "diligent"
    def __init__(self):
        super().__init__()
        self.exclude = [Lazy]


class Generous(Trait):
    name = "generous"
    def __init__(self):
        super().__init__()
        self.exclude = [Greedy]


class Gregarious(Trait):
    name = "gregarious"

    def __init__(self):
        super().__init__()
        self.exclude = [Shy]


class Greedy(Trait):
    name = "greedy"
    def __init__(self):
        super().__init__()
        self.exclude = [Generous]


class Honest(Trait):
    name = "Honest"

    def __init__(self):
        super().__init__()
        self.exclude = [Deceitful]


class Humble(Trait):
    name = "humble"

    def __init__(self):
        super().__init__()
        self.exclude = [Arrogant]


class Indolent(Trait):
    name = "indolent"


class Just(Trait):
    name = "just"

    def __init__(self):
        super().__init__()
        self.exclude = [Arbitrary]


class Lazy(Trait):
    name = "lazy"

    def ___init__(self):
        super().__init__()
        self.exclude = [Diligent]


class Lustful(Trait):
    name = "lustful"

    def ___init__(self):
        super().__init__()
        self.exclude = [Chaste]


class Shy(Trait):
    name = "shy"

    def __init__(self):
        super().__init__()
        self.exclude = [Gregarious]


trait_list = [Arbitrary, Arrogant, Brave, Chaste, Craven, Curious, Deceitful, Diligent,
              Generous, Gregarious, Greedy, Honest, Humble, Indolent, Just, Lazy, Lustful, Shy]
