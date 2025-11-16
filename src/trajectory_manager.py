import csv
import json
from types import new_class
import numpy as np
from math import atan2, pi

FIELDS = ["x", "y", "angle", "orientation", "direction", "action", "wea"]


def coordinates_to_json(
    coordinates: list,
    actions: list,
    is_angle: int,
    is_orientation: int,
    is_direction: int,
    is_action: int,
    is_wea: int,
):
    # Convert coordinates and add them to a json file

    coordinates = coordinates_to_int(coordinates)

    mask = [1, 1, is_angle, is_orientation, is_direction, is_action, is_wea]

    if mask[5] and len(actions) > 0:
        json_actions = format_actions_to_json(actions)
        trajectory = [
            json_actions,
            [
                dict(
                    zip(
                        [field for field, keep in zip(FIELDS, mask) if keep],
                        [val for val, keep in zip(value, mask) if keep],
                    )
                )
                for value in coordinates
            ],
        ]

    else:
        trajectory = [
            dict(
                zip(
                    [field for field, keep in zip(FIELDS, mask) if keep],
                    [val for val, keep in zip(value, mask) if keep],
                )
            )
            for value in coordinates
        ]

    return trajectory


def format_json_to_trajectory(json_data):
    """Convert the content of json_data into a trajectory list and an actions list"""

    formated_json_data = [[dict.get(key, None) for key in FIELDS] for dict in json_data]
    trajectory = coordinates_to_float64(formated_json_data)

    if trajectory:
        return trajectory


def coordinates_to_csv(
    coordinates: list,
    file_path: str,
    is_angle: str,
    is_orientation: str,
    is_direction: str,
    is_action: str,
):
    # Convert coordinates and add them to a csv file

    coordinates = coordinates_to_int(coordinates)

    mask = [
        True,
        True,
        is_angle.lower() == "true",
        is_orientation.lower() == "true",
        is_direction.lower() == "true",
        is_action.lower() == "true",
    ]

    coordinates = [
        [val for val, keep in zip(value, mask) if keep] for value in coordinates
    ]

    with open(file_path, mode="w", newline="") as file:
        # Create header and add coordinates to a csv file
        writer = csv.writer(file)
        writer.writerow(header for header, keep in zip(FIELDS, mask) if keep)
        writer.writerows(coordinates)


def csv_to_coordinates(file_path: str):
    # Convert the content of a csv file to coordinates array
    # TODO: import the trajectory depending of the header of the csv

    with open(file_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        coordinates = [[None if cell == "" else cell for cell in row] for row in reader]
        coordinates = coordinates_to_float64(coordinates)

    if coordinates:
        return coordinates


def format_actions_to_json(actions: list[str]) -> dict[str, str]:
    """Convert a list of actions in a list of dict that can be read easily for a json_file

    Args:
        actions (list[str]): a list of actions that can be set for a point

    Returns:
        json_action (list[dict[str, str]]): the formated actions that can be saved inside a json_file
    """

    json_actions = dict(
        zip(
            [f"action {i}" for i in range(len(actions))],
            [action for action in actions],
        )
    )

    return json_actions


def format_json_to_actions(json_data) -> list[str]:
    actions = [action for action in json_data.values()]

    return actions


def update_trajectory(image_point, point_idx: int, values_index: int, new_values):
    """Update the trajectory idx based on the updated_index list and the new_values list"""

    image_point[point_idx][values_index] = new_values

    return image_point


def calculate_angle(coordinates: list):
    # Calculate the angle between two points in a list of coordinates

    if len(coordinates) < 2:
        return coordinates
    coordinates = coordinates_to_int(coordinates)
    trajectory_points = [
        [
            x,
            y,
            atan2(coordinates[i + 1][1] - y, coordinates[i + 1][0] - x) * 180 / pi,
            orientation,
            direction,
            action,
            wea,
        ]
        for i, (x, y, _, orientation, direction, action, wea) in enumerate(
            coordinates[:-1]
        )
    ]
    trajectory_points.append(coordinates[-1])
    return trajectory_points


def coordinates_to_int(coordinates: list):
    # Convert and round all coordinates from np.float64 to int

    return [
        [int(round(coordinate)) for coordinate in sublist[:2]] + sublist[2:]
        for sublist in coordinates
    ]


def coordinates_to_float64(coordinates: list):
    # Convert all coordinates from int to np.float64

    return [
        [np.float64(coordinate) for coordinate in sublist[:2]]
        + [float(value) if value is not None else None for value in sublist[2:-3]]
        + sublist[-3:]
        for sublist in coordinates
    ]
