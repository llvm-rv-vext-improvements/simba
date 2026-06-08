from typing import TypeVar, Type

from pydantic import ValidationError, FilePath, BaseModel


M = TypeVar("M", bound=BaseModel)


def parse_json(cls: Type[M], path: FilePath) -> M:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
            return cls.model_validate_json(data)
    except ValidationError as e:
        message = ", ".join([f'{err["loc"][0]} {err["type"]}' for err in e.errors()])
        raise ValueError(f"failed to parse config: {message}") from e
    except Exception as e:
        raise RuntimeError(f"failed to read config: {e}") from e
