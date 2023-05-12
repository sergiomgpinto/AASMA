class Environment:
    def __init__(self):
        self.initial_state = None
        self.current_state = None

    def transformer(self, state):
        raise NotImplementedError()
