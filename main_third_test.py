from main import combine_first_name_and_last_name


def test_combine_first_name_and_last_name() -> None:
    res = combine_first_name_and_last_name("hidayat", "hamir")
    assert res == "hidayat hamir"


def test_combine_first_name_and_last_name_fn_is_none() -> None:
    res = combine_first_name_and_last_name(None, "hamir")
    assert res == "hamir"


def test_combine_first_name_and_last_name_ln_is_none() -> None:
    res = combine_first_name_and_last_name("hidayat", None)
    assert res == "hidayat"


def test_combine_first_name_and_last_name_fn_ln_is_none() -> None:
    res = combine_first_name_and_last_name(None, None)
    assert res == ""


def test_combine_first_name_and_last_name_fn_is_empty() -> None:
    res = combine_first_name_and_last_name("", "hamir")
    assert res == "hamir"


def test_combine_first_name_and_last_name_ln_is_empty() -> None:
    res = combine_first_name_and_last_name("hidayat", "")
    assert res == "hidayat"


def test_combine_first_name_and_last_name_fn_ln_is_empty() -> None:
    res = combine_first_name_and_last_name("", "")
    assert res == ""
