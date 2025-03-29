import random
from copy import deepcopy

from utils import Resource, read_data, write_output

# from tqdm import tqdm


def run(input_file_name: str) -> None:
    best_score = 0
    best_output = None

    orig_D, orig_R, orig_T, orig_resources, orig_turns = read_data(input_file_name)
    orig_resources = {res.id: res for res in orig_resources.values() if res.type != "X"}

    # for try_idx in tqdm(range(1000)):
    for try_idx in range(100):
        print(f"Try {try_idx}")
        D, turns = (
            orig_D,
            deepcopy(orig_turns),
        )
        output = []
        score = 0
        current_resources: list[Resource] = []

        for idx, turn in enumerate(turns):
            # purchase resources
            purchased_resources = []
            purchase_cost = 0
            current_powered_buildings = sum(
                res.power
                for res in current_resources
                if res.activated
                and not res.dead
                and res.tick % (res.active_turns + res.inactive_turns)
                < res.active_turns
            )

            sampled_resources: list[Resource] = random.choices(
                list(orig_resources.values()),
                k=12,
            )

            sampled_resources = sorted(
                sampled_resources,
                key=lambda x: (
                    x.power
                    * (
                        x.total_turns
                        / (x.active_turns + x.inactive_turns)
                        * x.active_turns
                    ),
                    -x.periodic_cost * x.total_turns
                    - x.activation_cost
                    + (100 if x.type == "E" else 0),
                ),
                reverse=True,
            )

            for res in sampled_resources:
                if (
                    res.activation_cost + purchase_cost <= D
                    and current_powered_buildings + res.power <= turn.max_buildings
                    and len(purchased_resources) < 7
                ):
                    current_powered_buildings += res.power
                    purchase_cost += res.activation_cost
                    res.activated = True
                    purchased_resources.append(res.id)

            if purchased_resources:
                output.append(
                    f"{idx} {len(purchased_resources)} {' '.join(map(str, purchased_resources))}"
                )

            current_resource_count = len(current_resources)

            # purchase resources
            purchase_cost = 0
            for res_id in purchased_resources:
                res = deepcopy(orig_resources[res_id])
                purchase_cost += res.activation_cost
                res.activated = True
                current_resources.append(res)

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
            # apply E effects
            to_accumulate = 0
            if powered_buildings >= turn.min_buildings:
                profit = turn.unit_profit * min(powered_buildings, turn.max_buildings)

                if powered_buildings > turn.max_buildings:
                    to_accumulate = turn.max_buildings - powered_buildings

                    for res in current_resources:
                        if (
                            res.activated
                            and not res.dead
                            and res.tick % (res.active_turns + res.inactive_turns)
                            < res.active_turns
                            and res.type == "E"
                        ):
                            available_to_store = min(
                                to_accumulate, res.effect_value - res.e_type_value
                            )

                            res.e_type_value += available_to_store
                            to_accumulate -= available_to_store
            else:
                needed = turn.min_buildings - powered_buildings
                first_pass_needed = needed

                for res in current_resources:
                    if (
                        res.activated
                        and not res.dead
                        and res.tick % (res.active_turns + res.inactive_turns)
                        < res.active_turns
                        and res.type == "E"
                    ):
                        available_to_use = min(first_pass_needed, res.e_type_value)

                        first_pass_needed -= available_to_use

                if first_pass_needed == 0:
                    for res in current_resources:
                        if (
                            res.activated
                            and not res.dead
                            and res.tick % (res.active_turns + res.inactive_turns)
                            < res.active_turns
                            and res.type == "E"
                        ):
                            available_to_use = min(first_pass_needed, res.e_type_value)
                            res.e_type_value -= available_to_use
                            needed -= available_to_use

                    profit = turn.unit_profit * turn.min_buildings

            score += profit

            D += profit - purchase_cost - maintenance_cost

            e_value_to_distribute = 0
            for res in current_resources:
                if res.activated:
                    res.tick += 1

                if res.tick == res.total_turns:
                    res.dead = True

                    if res.type == "E":
                        e_value_to_distribute += res.e_type_value

            for res in current_resources:
                if not res.dead and res.type == "E":
                    can_get_e_value = min(
                        e_value_to_distribute, res.effect_value - res.e_type_value
                    )

                    res.e_type_value += can_get_e_value
                    e_value_to_distribute -= can_get_e_value

        final_output = "\n".join(output)
        # final_score = calculate_score(input_file_name, final_output)
        final_score = score
        # print(final_score)

        if final_score >= best_score:
            best_score = final_score
            best_output = final_output

    print(f"Best score for {input_file_name}: {best_score}")

    write_output(best_output, input_file_name)


if __name__ == "__main__":
    for input_file_name in [
        # "0-demo",
        # "1-thunberg",
        # "2-attenborough",
        # "3-goodall",
        # "4-maathai",
        # "5-carson",
        # "6-earle",
        # "7-mckibben",
        "8-shiva",
    ]:
        run(input_file_name)
