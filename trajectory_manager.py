import csv
import json
from types import new_class
import numpy as np
from math import atan2, pi

FIELDS = ["x", "y", "angle", "orientation", "direction", "action"]


def coordinates_to_json(
    coordinates: list,
    actions: list,
    file_path: str,
    is_angle: str,
    is_orientation: str,
    is_direction: str,
    is_action: str,
):
    # Convert coordinates and add them to a json file

    coordinates = coordinates_to_int(coordinates)

    mask = [
        True,
        True,
        is_angle.lower() == "true",
        is_orientation.lower() == "true",
        is_direction.lower() == "true",
        is_action.lower() == "true",
    ]

    if mask[5]:
        trajectory = [
            [
                dict(
                    zip(
                        [f"action {i}" for i in range(len(actions))],
                        [action for action in actions],
                    )
                )
            ],
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

    with open(file_path, mode="w") as file:
        json.dump(trajectory, file, indent=4)


def json_to_coordinates(file_path: str):
    """Convert the content of a json file into a trajectory list and an actions list"""

    with open(file_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    if isinstance(json_data[0], dict):
        actions = []
        formated_json_data = [
            [dict.get(key, None) for key in FIELDS] for dict in json_data
        ]
        trajectory = coordinates_to_float64(formated_json_data)

    else:
        actions = [action for action in json_data.pop(0)[0].values()]
        formated_json_data = [
            [dict.get(key, None) for key in FIELDS] for dict in json_data[0]
        ]
        trajectory = coordinates_to_float64(formated_json_data)

    if trajectory:
        return trajectory, actions


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
        ]
        for i, (x, y, _, orientation, direction, action) in enumerate(coordinates[:-1])
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
        + [float(value) if value is not None else None for value in sublist[2:-2]]
        + sublist[-2:]
        for sublist in coordinates
    ]
