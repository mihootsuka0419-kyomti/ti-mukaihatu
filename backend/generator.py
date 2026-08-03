import random

from backend.data_loader import load_excuse_data


def choose_subject():
    data = load_excuse_data()
    return random.choice(data["subjects"])

def choose_object():
    data = load_excuse_data()
    return random.choice(data["objects"])

def choose_action(object_category):
    data = load_excuse_data()

    compatible_actions = []

    for action in data["actions"]:
        if object_category in action["compatible_categories"]:
            compatible_actions.append(action)

    return random.choice(compatible_actions)

def generate_pattern_1():
    data = load_excuse_data()

    subject = random.choice(data["subjects"])
    selected_object = random.choice(data["objects"])

    compatible_actions = []

    for action in data["actions"]:
        if selected_object["category"] in action["compatible_categories"]:
            compatible_actions.append(action)

    selected_action = random.choice(compatible_actions)

    return {
        "row_1": subject + "が",
        "row_2": selected_object["text"] + "を",
        "row_3": selected_action["text"] + "たため、",
    }

def generate_pattern_2():
    data = load_excuse_data()

    large_event = random.choice(data["large_events"])
    familiar_object = random.choice(data["familiar_objects"])

    compatible_actions = []

    for action in data["abnormal_actions"]:
        if familiar_object["category"] in action["compatible_categories"]:
            compatible_actions.append(action)

    abnormal_action = random.choice(compatible_actions)

    return {
        "row_1": large_event,
        "row_2": familiar_object["text"] + "が",
        "row_3": abnormal_action["text"] + "、",
    }

def generate_excuse():
    if random.choice([1, 2]) == 1:
        return generate_pattern_1()

    return generate_pattern_2()