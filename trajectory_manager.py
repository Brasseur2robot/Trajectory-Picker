import csv
import json
from types import new_class
import numpy as np
from math import atan2, pi

FIELDS = ["x", "y", "angle", "orientation", "direction"]


def coordinates_to_json(
    coordinates: list,
    file_path: str,
    is_angle: str,
    is_orientation: str,
    is_direction: str,
):
    # Convert coordinates and add them to a json file

    coordinates = coordinates_to_int(coordinates)

    mask = [
        True,
        True,
        is_angle.lower() == "true",
        is_orientation.lower() == "true",
        is_direction.lower() == "true",
    ]

    coordinates = [
        dict(
            zip(
                [field for field, keep in zip(FIELDS, mask) if keep],
                [val for val, keep in zip(value, mask) if keep],
            )
        )
        for value in coordinates
    ]

    with open(file_path, mode="w") as file:
        json.dump(coordinates, file, indent=4)


def json_to_coordinates(file_path: str):
    # Convert the content of a json file to coordinates array
    with open(file_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    json_data = [[dict.get(key, None) for key in FIELDS] for dict in json_data]
    json_data = coordinates_to_float64(json_data)
    print(json_data)

    if json_data:
        return json_data


def coordinates_to_csv(
    coordinates: list,
    file_path: str,
    is_angle: str,
    is_orientation: str,
    is_direction: str,
):
    # Convert coordinates and add them to a csv file

    coordinates = coordinates_to_int(coordinates)

    mask = [
        True,
        True,
        is_angle.lower() == "true",
        is_orientation.lower() == "true",
        is_direction.lower() == "true",
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


def update_trajectory(idx: int, image_point, updated_index: list, new_values: list):
    """Update the trajectory idx based on the updated_index list and the new_values list"""

    print(new_values[0])
    for i in range(len(updated_index)):
        image_point[idx][updated_index[i]] = new_values[i]

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
        ]
        for i, (x, y, _, orientation, direction) in enumerate(coordinates[:-1])
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
        + [float(value) if value is not None else None for value in sublist[2:-1]]
        + [sublist[-1]]
        for sublist in coordinates
    ]
