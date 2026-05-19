class BaseMenu:
    def __init__(self, app_context):
        self.app = app_context

    def render(self):
        raise NotImplementedError("Cada menu deve implementar o método render().")
