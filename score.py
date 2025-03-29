import os
from copy import deepcopy

from test_score import TEST_DATA
from utils import Resource, read_data


def calculate_score(file_name: str | None, data: str | None) -> int:
    turn_purchased_resources = {}
    all_used_types = set()

    if data is None:
        with open(os.path.join("output", f"{file_name}.txt")) as file:
            output = file.readlines()
            for line in output:
                tokens = line.split()
                idx = int(tokens[0])
                purchased_resources = list(map(int, tokens[2:]))
                turn_purchased_resources[idx] = purchased_resources
    else:
        for line in data.split("\n"):
            tokens = line.split()
            idx = int(tokens[0])
            purchased_resources = list(map(int, tokens[2:]))
            turn_purchased_resources[idx] = purchased_resources

    D, R, T, resources, turns = read_data(file_name)

    score = 0
    current_resources: list[Resource] = []
    for turn_idx in range(T):
        turn = turns[turn_idx]
        current_resource_count = len(current_resources)

        # purchase resources
        purchased_resources = turn_purchased_resources.get(turn_idx, [])
        purchase_cost = 0
        for res_id in purchased_resources:
            res = deepcopy(resources[res_id])
            purchase_cost += res.activation_cost
            res.activated = True
            current_resources.append(res)
            all_used_types.add(res.type)

        if purchase_cost > D:
            current_resources = current_resources[:current_resource_count]
            purchased_resources = []

        # measure special effects
        b_pos = 0
        b_neg = 0
        a_pos = 0
        a_neg = 0
        d_pos = 0
        d_neg = 0
        c_pos = 0
        c_neg = 0
        for res in current_resources:
            if (
                res.activated
                and not res.dead
                and res.tick % (res.active_turns + res.inactive_turns)
                < res.active_turns
            ):
                if res.type == "B":
                    if res.effect_value > 0:
                        b_pos += res.effect_value
                    else:
                        b_neg += res.effect_value
                elif res.type == "A":
                    if res.effect_value > 0:
                        a_pos += res.effect_value
                    else:
                        a_neg += res.effect_value
                elif res.type == "D":
                    if res.effect_value > 0:
                        d_pos += res.effect_value
                    else:
                        d_neg += res.effect_value
                elif res.type == "C":
                    if res.effect_value > 0:
                        c_pos += res.effect_value
                    else:
                        c_neg += res.effect_value

        # apply C effects
        for res_idx in range(current_resource_count, len(current_resources)):
            res = current_resources[res_idx]

            res.total_turns = max(
                1,
                res.total_turns + int(res.total_turns * (c_pos + c_neg) / 100),
            )

        # apply B effects
        turn.min_buildings = max(
            0,
            turn.min_buildings + int((b_pos + b_neg) / 100 * turn.min_buildings),
        )
        turn.max_buildings = max(
            0,
            turn.max_buildings + int((b_pos + b_neg) / 100 * turn.max_buildings),
        )

        # apply D effects
        turn.unit_profit = max(
            0,
            turn.unit_profit + int(turn.unit_profit * (d_pos + d_neg) / 100),
        )

        # calculate costs
        maintenance_cost = 0
        for res in current_resources:
            if res.activated and not res.dead:
                maintenance_cost += res.periodic_cost

        powered_buildings = 0
        for res in current_resources:
            if (
                res.activated
                and not res.dead
                and res.tick % (res.active_turns + res.inactive_turns)
                < res.active_turns
            ):
                k = res.power
                # apply A effects
                k = max(
                    0,
                    k + int(k * (a_pos + a_neg) / 100),
                )
                powered_buildings += k

        profit = 0
        if powered_buildings >= turn.min_buildings:
            profit = turn.unit_profit * min(powered_buildings, turn.max_buildings)

        # print("-" * 50)
        # print(
        #     f"Turn {turn_idx} ({turn.min_buildings}, {turn.max_buildings}): profit {profit}, purchase_cost {purchase_cost}, maintenance_cost {maintenance_cost}, powered_buildings {powered_buildings}"
        # )
        # for res in current_resources:
        #     print(
        #         f"Resource {res.id} ({res.activated}, {res.tick}, {res.dead}): {res.power}"
        #     )

        score += profit

        D += profit - purchase_cost - maintenance_cost

        for res in current_resources:
            if res.activated:
                res.tick += 1

            if res.tick == res.total_turns:
                res.dead = True

    # print(f"All used types: {all_used_types}")
    return score


if __name__ == "__main__":
    for file_name, data, expected in TEST_DATA[-2:-1]:
        print("-" * 50)
        received_score = calculate_score(file_name, data)
        assert received_score == expected, (
            f"Expected {expected}, but got {received_score} (diff is {expected - received_score})"
        )
