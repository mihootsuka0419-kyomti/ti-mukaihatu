import random

from backend.data_loader import load_excuse_data


def validate_start_category(data, start_category):
    """
    スタート画面から渡されたカテゴリーが、
    JSONに登録されているか確認する。
    """
    valid_categories = data.get(
        "start_categories",
        [],
    )

    if start_category not in valid_categories:
        raise ValueError(
            f"無効なスタートカテゴリーです: "
            f"{start_category}"
        )


def filter_by_start_category(
    items,
    start_category,
):
    """
    指定されたスタートカテゴリーに対応する素材だけを残す。
    """
    filtered_items = []

    for item in items:
        compatible_categories = item.get(
            "compatible_start_categories",
            [],
        )

        if start_category in compatible_categories:
            filtered_items.append(item)

    return filtered_items


def filter_by_allowed_categories(
    items,
    allowed_categories,
):
    """
    allowed_categoriesに含まれるカテゴリーの素材だけを残す。

    含まれないカテゴリーは、生成禁止として扱う。
    """
    filtered_items = []

    for item in items:
        if item["category"] in allowed_categories:
            filtered_items.append(item)

    return filtered_items


def choose_weighted_item(
    candidates,
    preferred_categories,
    normal_weight,
    preferred_weight,
):
    """
    許可された候補から、カテゴリーに応じて重み付き抽選する。

    preferred_categoriesに含まれる候補:
        preferred_weight

    それ以外の許可候補:
        normal_weight
    """
    if not candidates:
        raise ValueError(
            "重み付き抽選に使用できる候補がありません。"
        )

    weights = []

    for candidate in candidates:
        category = candidate["category"]

        if category in preferred_categories:
            weights.append(preferred_weight)
        else:
            weights.append(normal_weight)

    return random.choices(
        candidates,
        weights=weights,
        k=1,
    )[0]


def get_viable_actions(
    data,
    start_category,
):
    """
    通常形式で実際に生成可能な動作だけを返す。

    次の両方を満たす動作を候補とする。

    ・スタートカテゴリーに対応する主体が存在する
    ・スタートカテゴリーに対応する対象が存在する
    """
    start_subjects = filter_by_start_category(
        items=data["subjects"],
        start_category=start_category,
    )

    start_objects = filter_by_start_category(
        items=data["objects"],
        start_category=start_category,
    )

    viable_actions = []

    for action in data["actions"]:
        allowed_subjects = filter_by_allowed_categories(
            items=start_subjects,
            allowed_categories=(
                action["allowed_subject_categories"]
            ),
        )

        allowed_objects = filter_by_allowed_categories(
            items=start_objects,
            allowed_categories=(
                action["allowed_object_categories"]
            ),
        )

        if allowed_subjects and allowed_objects:
            viable_actions.append(action)

    return viable_actions


def get_viable_abnormal_actions(
    data,
    start_category,
):
    """
    大規模現象形式で実際に生成可能な異常状態だけを返す。

    次の両方を満たす異常状態を候補とする。

    ・対応する大規模現象が存在する
    ・スタートカテゴリーに対応する身近な対象が存在する
    """
    start_objects = filter_by_start_category(
        items=data["familiar_objects"],
        start_category=start_category,
    )

    viable_actions = []

    for abnormal_action in data["abnormal_actions"]:
        allowed_events = filter_by_allowed_categories(
            items=data["large_events"],
            allowed_categories=(
                abnormal_action["allowed_event_categories"]
            ),
        )

        allowed_objects = filter_by_allowed_categories(
            items=start_objects,
            allowed_categories=(
                abnormal_action["allowed_object_categories"]
            ),
        )

        if allowed_events and allowed_objects:
            viable_actions.append(abnormal_action)

    return viable_actions


def generate_pattern_1(
    data,
    start_category,
):
    """
    通常形式を生成する。

    主体が
    対象を
    動作したため、
    """
    settings = data["generation_settings"]

    normal_weight = settings["normal_weight"]
    preferred_weight = settings["preferred_weight"]

    viable_actions = get_viable_actions(
        data=data,
        start_category=start_category,
    )

    if not viable_actions:
        raise ValueError(
            "通常形式で生成できる組み合わせがありません。"
        )

    selected_action = random.choice(
        viable_actions
    )

    start_subjects = filter_by_start_category(
        items=data["subjects"],
        start_category=start_category,
    )

    start_objects = filter_by_start_category(
        items=data["objects"],
        start_category=start_category,
    )

    allowed_subjects = filter_by_allowed_categories(
        items=start_subjects,
        allowed_categories=(
            selected_action["allowed_subject_categories"]
        ),
    )

    allowed_objects = filter_by_allowed_categories(
        items=start_objects,
        allowed_categories=(
            selected_action["allowed_object_categories"]
        ),
    )

    selected_subject = choose_weighted_item(
        candidates=allowed_subjects,
        preferred_categories=(
            selected_action[
                "preferred_subject_categories"
            ]
        ),
        normal_weight=normal_weight,
        preferred_weight=preferred_weight,
    )

    selected_object = choose_weighted_item(
        candidates=allowed_objects,
        preferred_categories=(
            selected_action[
                "preferred_object_categories"
            ]
        ),
        normal_weight=normal_weight,
        preferred_weight=preferred_weight,
    )

    row_1 = selected_subject["text"] + "が"
    row_2 = selected_object["text"] + "を"
    row_3 = selected_action["text"] + "ため、"

    return {
        "pattern": "pattern_1",
        "start_category": start_category,
        "row_1": row_1,
        "row_2": row_2,
        "row_3": row_3,
        "generated_text": (
            row_1
            + row_2
            + row_3
        ),
    }


def generate_pattern_2(
    data,
    start_category,
):
    """
    大規模現象形式を生成する。

    大規模現象の影響で、
    身近な対象が
    異常な状態になり、
    """
    settings = data["generation_settings"]

    normal_weight = settings["normal_weight"]
    preferred_weight = settings["preferred_weight"]

    viable_actions = get_viable_abnormal_actions(
        data=data,
        start_category=start_category,
    )

    if not viable_actions:
        raise ValueError(
            "大規模現象形式で生成できる"
            "組み合わせがありません。"
        )

    selected_action = random.choice(
        viable_actions
    )

    start_objects = filter_by_start_category(
        items=data["familiar_objects"],
        start_category=start_category,
    )

    allowed_events = filter_by_allowed_categories(
        items=data["large_events"],
        allowed_categories=(
            selected_action["allowed_event_categories"]
        ),
    )

    allowed_objects = filter_by_allowed_categories(
        items=start_objects,
        allowed_categories=(
            selected_action["allowed_object_categories"]
        ),
    )

    selected_event = choose_weighted_item(
        candidates=allowed_events,
        preferred_categories=(
            selected_action[
                "preferred_event_categories"
            ]
        ),
        normal_weight=normal_weight,
        preferred_weight=preferred_weight,
    )

    selected_object = choose_weighted_item(
        candidates=allowed_objects,
        preferred_categories=(
            selected_action[
                "preferred_object_categories"
            ]
        ),
        normal_weight=normal_weight,
        preferred_weight=preferred_weight,
    )

    row_1 = selected_event["text"]
    row_2 = selected_object["text"] + "が"
    row_3 = selected_action["text"]

    return {
        "pattern": "pattern_2",
        "start_category": start_category,
        "row_1": row_1,
        "row_2": row_2,
        "row_3": row_3,
        "generated_text": (
            row_1
            + row_2
            + row_3
        ),
    }


def generate_excuse(start_category):
    """
    スタートカテゴリーに対応した言い訳を生成する。

    通常形式と大規模現象形式は原則50%ずつで選ぶ。
    片方に生成可能な候補がない場合は、
    生成可能な形式だけを使用する。
    """
    data = load_excuse_data()

    validate_start_category(
        data=data,
        start_category=start_category,
    )

    viable_patterns = []

    if get_viable_actions(
        data=data,
        start_category=start_category,
    ):
        viable_patterns.append("pattern_1")

    if get_viable_abnormal_actions(
        data=data,
        start_category=start_category,
    ):
        viable_patterns.append("pattern_2")

    if not viable_patterns:
        raise ValueError(
            "指定されたカテゴリーで生成できる"
            "言い訳がありません。"
        )

    selected_pattern = random.choice(
        viable_patterns
    )

    if selected_pattern == "pattern_1":
        return generate_pattern_1(
            data=data,
            start_category=start_category,
        )

    return generate_pattern_2(
        data=data,
        start_category=start_category,
    )