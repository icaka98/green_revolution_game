from utils import read_data, write_output


def run(input_file_name: str) -> None:
    D, R, T, resources, turns = read_data(input_file_name)
    output = []

    for idx, turn in enumerate(turns):
        powered_buildings = 0

        # purchase resources
        purchased_resources = []
        purchase_cost = 0
        for res in resources.values():
            if not res.activated and res.activation_cost + purchase_cost <= D:
                purchase_cost += res.activation_cost
                res.activated = True
                purchased_resources.append(res.id)

        if purchased_resources:
            output.append(
                f"{idx} {len(purchased_resources)} {' '.join(map(str, purchased_resources))}"
            )

    write_output(output, input_file_name)


if __name__ == "__main__":
    for input_file_name in [
        "0-demo",
        # "1-thunberg",
        # "2-attenborough",
        # "3-goodall",
        # "4-maathai",
        # "5-carson",
        # "6-earle",
        # "7-mckibben",
        # "8-shiva",
    ]:
        run(input_file_name)
