import csv
import json
import numpy as np
from math import atan2, pi


def coordinates_to_json(coordinates: list, file_path: str):
    # Convert coordinates and add them to a json file

    coordinates = coordinates_to_int(coordinates)

    with open(file_path, mode="w") as file:
        json.dump(coordinates, file, indent=4)


def json_to_coordinates(file_path: str):
    # Convert the content of a json file to coordinates array
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    data = coordinates_to_float64(data)

    if data:
        return data


def coordinates_to_csv(coordinates: list, file_path: str):
    # Convert coordinates and add them to a csv file

    coordinates = coordinates_to_int(coordinates)

    with open(file_path, mode="w", newline="") as file:
        # Create header and add coordinates to a csv file
        writer = csv.writer(file)
        writer.writerow(["x", "y", "angle"])
        writer.writerows(coordinates)


def csv_to_coordinates(file_path: str):
    # Convert the content of a csv file to coordinates array
    coordinates = []
    with open(file_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["angle"] == "":
                coordinates.append((row["x"], row["y"], None))
            else:
                coordinates.append((row["x"], row["y"], row["angle"]))
        coordinates = coordinates_to_float64(coordinates)

    if coordinates:
        return coordinates


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
        return coordinates
    coordinates = coordinates_to_int(coordinates)
    trajectory_points = [
        (x, y, atan2(coordinates[i + 1][1] - y, coordinates[i + 1][0] - x) * 180 / pi)
        for i, (x, y, _) in enumerate(coordinates[:-1])
    ]
    trajectory_points.append(coordinates[-1])
    return trajectory_points


def coordinates_to_int(coordinates: list):
    # Convert and round all coordinates from np.float64 to int
    return [
        tuple(int(round(coordinate)) for coordinate in sublist[:2]) + (sublist[2],)
        for sublist in coordinates
    ]


def coordinates_to_float64(coordinates: list):
    # Convert all coordinates from int to np.float64
    return [
        tuple(np.float64(coordinate) for coordinate in sublist[:2])
        + (float(sublist[2]) if sublist[2] is not None else None,)
        for sublist in coordinates
    ]
