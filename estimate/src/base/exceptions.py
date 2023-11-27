class NotFound(Exception):
    pass


class InvalidInput(Exception):
    pass


class InvalidFilter(Exception):
    def __init__(self, attr: str):
        super().__init__(f'Received invalid filter "{attr}"')
