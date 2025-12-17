import csv
import json
from types import new_class
import numpy as np
from math import atan2, pi

FIELDS = ["x", "y", "angle", "orientation", "direction", "action", "wea"]


def coordinates_to_json(
    coordinates: list,
    actions: list,
    fbd_area: list,
    is_angle: int,
    is_orientation: int,
    is_direction: int,
    is_action: int,
    is_export_action: int,
    is_wea: int,
    is_fbd_area: int,
    is_export_fbd_area: int,
):
    # Convert coordinates and add them to a json file

    coordinates = coordinates_to_int(coordinates)

    mask = [
        1,
        1,
        is_angle,
        is_orientation,
        is_direction,
        is_action,
        is_wea,
    ]

    if (
        is_action
        and not is_export_action
        and len(actions) > 0
        and is_fbd_area
        and not is_export_fbd_area
        and len(fbd_area) > 0
    ):
        json_actions = format_actions_to_json(actions)
        json_fbd_area = format_fbd_area_to_json(fbd_area)
        formated_data = [
            json_actions,
            json_fbd_area,
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
        json_data = {
            "metadata": {"content_type": "trajectory_action_fbd_area"},
            "data": formated_data,
        }

    elif is_action and not is_export_action and len(actions) > 0:
        json_actions = format_actions_to_json(actions)
        formated_data = [
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
        json_data = {
            "metadata": {"content_type": "trajectory_action"},
            "data": formated_data,
        }

    elif is_fbd_area and not is_export_fbd_area and len(fbd_area) > 0:
        json_fbd_area = format_fbd_area_to_json(fbd_area)
        formated_data = [
            json_fbd_area,
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
        json_data = {
            "metadata": {"content_type": "trajectory_fbd_area"},
            "data": formated_data,
        }

    else:
        formated_trajectory = [
            dict(
                zip(
                    [field for field, keep in zip(FIELDS, mask) if keep],
                    [val for val, keep in zip(value, mask) if keep],
                )
            )
            for value in coordinates
        ]
        json_data = {
            "metadata": {"content_type": "trajectory"},
            "data": formated_trajectory,
        }

    return json_data


def format_json_to_trajectory(json_data):
    """Convert the content of json_data into a trajectory list and an actions list"""

    formated_json_data = [[dict.get(key, None) for key in FIELDS] for dict in json_data]
    trajectory = coordinates_to_float64(formated_json_data)

    if trajectory:
        return trajectory


def format_actions_to_json(
    actions: list[str], is_json_data: bool = False
) -> dict[str, str]:
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

    if is_json_data:
        json_data = {
            "metadata": {"content_type": "action"},
            "data": json_actions,
        }

        return json_data

    return json_actions


def format_json_to_actions(json_data) -> list[str]:
    actions = [action for action in json_data.values()]

    return actions


def format_fbd_area_to_json(
    fbd_area: list[list[int, int, int, int, int]], is_json_data: bool = False
) -> list[dict[str, int]]:
    """Convert a list of coordinates for the forbiden area in a list of dict that can be read easily for a json_file

    Args:
        fbd_area (list[list[int, int, int, int, int]]): all fbd_areas to parse to a json readable format
    """

    keys = ["x1", "y1", "x2", "y2"]

    json_fbd_area = [dict(zip(keys, row[:-1])) for row in fbd_area]

    if is_json_data:
        json_data = {
            "metadata": {"content_type": "fbd_area"},
            "data": json_fbd_area,
        }

        return json_data

    return json_fbd_area


def format_json_to_fbd_area(
    json_data: list[dict[str, int]],
) -> list[list[int, int, int, int, int]]:
    """Convert a formated fbd_area for json back to a list of list of int

    Args:
        json_data (list[dict[str, int]]): the json formated content that is read by the program
    """

    fbd_area = [[*dict.values(), -1] for dict in json_data]

    return fbd_area


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
