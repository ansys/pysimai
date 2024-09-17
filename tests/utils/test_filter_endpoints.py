import ansys.simai.core.utils.filter_endpoints as fe


def test_to_raw_filters_dict():
    filters = fe.to_raw_filters({"name": "paul", "production_capacity": "6e34Kg"})
    assert filters == [
        {"field": "name", "operator": "EQ", "value": "paul"},
        {"field": "production_capacity", "operator": "EQ", "value": "6e34Kg"},
    ]


def test_to_raw_filters_list():
    filters = fe.to_raw_filters([("name", "EQ", "paul"), ("production_capacity", "GTE", 10**10)])
    assert filters == [
        {"field": "name", "operator": "EQ", "value": "paul"},
        {"field": "production_capacity", "operator": "GTE", "value": 10**10},
    ]


def test_to_raw_filters_none():
    assert fe.to_raw_filters(None) is None
