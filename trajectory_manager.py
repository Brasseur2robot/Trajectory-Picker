import csv
import json
import numpy as np
from math import atan2, pi


def coordinates_to_json(coordinates: list, filepath):
    # Convert coordinates and add them to a json file

    coordinates = np_float_to_int(coordinates)

    with open(filepath, mode="w") as file:
        json.dump(coordinates, file, indent=4)


def coordinates_to_csv(coordinates: list, filepath):
    # Convert coordinates and add them to a csv file

    print(type(filepath))

    coordinates = np_float_to_int(coordinates)

    with open(filepath, mode="w", newline="") as file:
        # Create header and add coordinates to a csv file
        writer = csv.writer(file)
        writer.writerow(["x", "y"])
        writer.writerows(coordinates)


def update_coordinates(idx: int, image_point, entry_widgets: list):
    # Update the coordinates list when the user changes a value
    x_entry, y_entry = entry_widgets[2 * idx], entry_widgets[2 * idx + 1]

    if not isinstance(x_entry.get(), float) or isinstance(y_entry.get(), float):
        return image_point

    new_x = np.float64(x_entry.get())
    new_y = np.float64(y_entry.get())
    image_point[idx] = (new_x, new_y)

    return image_point


def calculate_angle(coordinates: list):
    # Calculate the angle between two points in a list of coordinates
    if len(coordinates) < 2:
        return None
    coordinates = np_float_to_int(coordinates)
    trajectory_points = [
        (x, y, atan2(coordinates[i + 1][1] - y, coordinates[i + 1][0] - x) * 180 / pi)
        for i, (x, y) in enumerate(coordinates[:-1])
    ]


def np_float_to_int(coordinates: list):
    # Convert and round all coordinates
    return [
        [int(round(coordinate)) for coordinate in sublist] for sublist in coordinates
    ]
