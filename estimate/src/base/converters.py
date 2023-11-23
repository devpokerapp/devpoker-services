from uuid import UUID


def from_uuid(value: str):
    return UUID(value)


def from_str(value: str):
    return value


def from_bool(value: str):
    return value.lower() == "true"
