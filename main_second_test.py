from main import (
    is_form_code_valid,
    get_code_from_form,
    is_form_phone_valid,
    get_phone_from_form,
    get_list_from_form,
)
from werkzeug.datastructures import MultiDict


def test_is_form_code_valid_expected() -> None:
    res = is_form_code_valid(
        MultiDict(
            {
                "first": "",
                "second": "",
                "third": "",
                "fourth": "",
                "fifth": "",
            }
        )
    )
    assert res


def test_is_form_code_valid_without_fifth() -> None:
    res = is_form_code_valid(
        MultiDict(
            {
                "first": "",
                "second": "",
                "third": "",
                "fourth": "",
            }
        )
    )
    assert not res


def test_is_form_code_valid_without_fourth() -> None:
    res = is_form_code_valid(
        MultiDict(
            {
                "first": "",
                "second": "",
                "third": "",
                "fifth": "",
            }
        )
    )
    assert not res


def test_is_form_code_valid_expected_without_third() -> None:
    res = is_form_code_valid(
        MultiDict(
            {
                "first": "",
                "second": "",
                "fourth": "",
                "fifth": "",
            }
        )
    )
    assert not res


def test_is_form_code_valid_without_second() -> None:
    res = is_form_code_valid(
        MultiDict(
            {
                "first": "",
                "third": "",
                "fourth": "",
                "fifth": "",
            }
        )
    )
    assert not res


def test_is_form_code_valid_without_first() -> None:
    res = is_form_code_valid(
        MultiDict(
            {
                "second": "",
                "third": "",
                "fourth": "",
                "fifth": "",
            }
        )
    )
    assert not res


def test_get_code_from_form_expected() -> None:
    res = get_code_from_form(
        MultiDict(
            {
                "first": "4",
                "second": "2",
                "third": "4",
                "fourth": "3",
                "fifth": "5",
            }
        )
    )
    assert res == "42435"


def test_get_code_from_form_with_empty() -> None:
    res = get_code_from_form(
        MultiDict(
            {
                "first": "",
                "second": "2",
                "third": "4",
                "fourth": "3",
                "fifth": "5",
            }
        )
    )
    assert res == "2435"


def test_is_form_phone_valid_valid() -> None:
    res = is_form_phone_valid(MultiDict({"phone": "082151352437"}))
    assert res


def test_is_form_phone_valid_not_valid() -> None:
    res = is_form_phone_valid(MultiDict({}))
    assert not res


def test_get_phone_from_form_expected() -> None:
    res = get_phone_from_form(MultiDict({"phone": "82151352437"}))
    assert res == "+6282151352437"


def test_get_phone_from_form_empty() -> None:
    res = get_phone_from_form(MultiDict({"phone": ""}))
    assert res == "+62"


def test_get_list_from_form_expected() -> None:
    res = get_list_from_form(
        MultiDict({"new_senders": ["1234", "2345", "3456"]}),
        "new_senders",
    )
    assert res == [1234, 2345, 3456]


def test_get_list_from_form_empty() -> None:
    res = get_list_from_form(
        MultiDict({"new_senders": []}),
        "new_senders",
    )
    assert res == []
