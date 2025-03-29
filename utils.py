import os
from dataclasses import dataclass


@dataclass
class Resource:
    id: int
    activation_cost: int
    periodic_cost: int
    active_turns: int
    inactive_turns: int
    total_turns: int
    power: int
    type: str
    effect_value: int | None = None
    tick: int = 0
    activated: bool = False
    dead: bool = False
    score: int = 0
    e_type_value: int = 0


@dataclass
class Turn:
    min_buildings: int
    max_buildings: int
    unit_profit: int


def read_data(input_name: str) -> tuple[int, int, int, dict[int, Resource], list[Turn]]:
    with open(os.path.join("input", f"{input_name}.txt")) as file:
        data = file.readlines()

    D, R, T = map(int, data[0].split())
    resources = {}
    for line in data[1 : R + 1]:
        tokens = line.split()

        resource_id = int(tokens[0])

        resource = Resource(
            resource_id,
            int(tokens[1]),
            int(tokens[2]),
            int(tokens[3]),
            int(tokens[4]),
            int(tokens[5]),
            int(tokens[6]),
            tokens[7],
        )

        if len(tokens) == 9:
            resource.effect_value = int(tokens[8])

        resources[resource_id] = resource

    turns = []
    for line in data[R + 1 :]:
        tokens = line.split()
        turn = Turn(int(tokens[0]), int(tokens[1]), int(tokens[2]))
        turns.append(turn)

    return D, R, T, resources, turns


def write_output(output: str, input_name: str) -> None:
    with open(os.path.join("output", f"{input_name}-3.txt"), "w+") as file:
        file.write(output)
