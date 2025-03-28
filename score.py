import math
import os
from copy import deepcopy

from utils import Resource, read_data


def calculate_score(file_name: str) -> int:
    turn_purchased_resources = {}
    with open(os.path.join("output", f"{file_name}.txt")) as file:
        output = file.readlines()
        for line in output:
            tokens = line.split()
            idx = int(tokens[0])
            purchased_resources = list(map(int, tokens[2:]))
            turn_purchased_resources[idx] = purchased_resources

    D, R, T, resources, turns = read_data(file_name)

    score = 0
    current_resources: list[Resource] = []
    for turn_idx in range(T):
        turn = turns[turn_idx]

        # purchase resources
        purchased_resources = turn_purchased_resources.get(turn_idx, [])
        purchase_cost = 0
        for res_id in purchased_resources:
            res = deepcopy(resources[res_id])
            purchase_cost += res.activation_cost
            res.activated = True
            current_resources.append(res)

        if purchase_cost > D:
            purchased_resources = []

        # measure special effects
        b_pos = 0
        b_neg = 0
        a_pos = 0
        a_neg = 0
        d_pos = 0
        d_neg = 0
        for res in current_resources:
            if res.activated and not res.dead:
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

        # apply B effects
        turn.min_buildings = max(
            0,
            turn.min_buildings
            + int(math.floor((b_pos - b_neg) / 100 * turn.min_buildings)),
        )
        turn.max_buildings = max(
            0,
            turn.max_buildings
            + int(math.floor((b_pos - b_neg) / 100 * turn.max_buildings)),
        )

        # apply D effects
        turn.unit_profit = max(
            0,
            turn.unit_profit
            + int(math.floor(turn.unit_profit * (d_pos - d_neg) / 100)),
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
                k = max(
                    0,
                    k + int(math.floor(k * (a_pos - a_neg) / 100)),
                )
                # powered_buildings += k

        # apply A effects
        powered_buildings = max(
            0,
            powered_buildings
            + int(math.floor(powered_buildings * (a_pos - a_neg) / 100)),
        )

        profit = 0
        if powered_buildings >= turn.min_buildings:
            profit = turn.unit_profit * min(powered_buildings, turn.max_buildings)

        # print("-" * 50)
        print(
            f"Turn {turn_idx} ({turn.min_buildings}, {turn.max_buildings}): profit {profit}, purchase_cost {purchase_cost}, maintenance_cost {maintenance_cost}, powered_buildings {powered_buildings}"
        )
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

    return score


if __name__ == "__main__":
    # score = calculate_score("1-thunberg")
    score = calculate_score("2-attenborough")

    print(score)
