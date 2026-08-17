import os  # unused import — ruff should flag this (F401)


def greet(name: str) -> str:
    return "hello " + name


x: int = "this is not an int"  # error: pyright should flag this type mismatch

print(greet("world"))
