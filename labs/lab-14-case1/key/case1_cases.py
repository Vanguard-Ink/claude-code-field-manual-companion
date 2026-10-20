"""The H1 cases: default-output renders of both menu() methods. Each case is
(name, issue key, property, kwargs). Goldens come from the pinned code."""

LINK = [
    ("link_default", "i1", "status", {}),
    ("link_value_none_issue3", "i3", "status", {}),
    ("link_value_minus1", "i1", "status", {"value": "-1"}),
    ("link_value_explicit", "i1", "status", {"value": "4"}),
    ("link_retired_current", "i2", "status", {}),
    ("link_showid", "i1", "status", {"showid": 1}),
    ("link_size", "i1", "status", {"size": 6}),
    ("link_height", "i1", "status", {"height": 3}),
    ("link_sort_str", "i1", "priority", {"sort_on": "-name"}),
    ("link_sort_tuple", "i1", "priority", {"sort_on": ("+", "order")}),
    ("link_additional", "i1", "assignedto", {"additional": ["realname"]}),
    ("link_html_kwargs", "i1", "status",
     {"html_kwargs": {"id": "st", "class": "x"}}),
    ("link_showdef", "i1", "status", {"showdef": " (default)"}),
    ("link_no_translate", "i1", "status", {"translate": False}),
    ("link_condition", "i1", "priority", {"name": "bug"}),
]

MULTI = [
    ("ml_default", "i1", "keyword", {}),
    ("ml_empty", "i3", "nosy", {}),
    ("ml_retired_current", "i3", "keyword", {}),
    ("ml_value_list", "i1", "keyword", {"value": ["4"]}),
    ("ml_value_empty_list", "i1", "keyword", {"value": []}),
    ("ml_showid", "i1", "keyword", {"showid": 1}),
    ("ml_size", "i1", "keyword", {"size": 8}),
    ("ml_height", "i1", "keyword", {"height": 2}),
    ("ml_sort_str", "i1", "keyword", {"sort_on": "-name"}),
    ("ml_sort_tuple", "i1", "keyword", {"sort_on": ("-", "id")}),
    ("ml_additional", "i1", "nosy", {"additional": ["realname"]}),
    ("ml_html_kwargs", "i1", "keyword", {"html_kwargs": {"id": "kw"}}),
    ("ml_no_translate", "i1", "keyword", {"translate": False}),
    ("ml_condition", "i1", "keyword", {"name": "db"}),
    ("ml_nosy_default", "i1", "nosy", {}),
]

CASES = LINK + MULTI
