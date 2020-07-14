import copy
import pytest

from pypinfo import core

ROWS = [
    ['python_version', 'percent', 'download_count'],
    ['2.7', '51.7%', '342250'],
    ['3.6', '21.1%', '139745'],
    ['3.5', '17.2%', '114254'],
    ['3.4', '7.6%', '50584'],
    ['3.3', '1.0%', '6666'],
    ['3.7', '0.7%', '4516'],
    ['2.6', '0.7%', '4451'],
    ['3.2', '0.0%', '138'],
    ['None', '0.0%', '13'],
]


def test_create_config():
    # Act
    config = core.create_config()

    # Assert
    assert config.use_legacy_sql


@pytest.mark.parametrize(
    "test_input, expected", [("pypinfo", "pypinfo"), ("setuptools_scm", "setuptools-scm"), ("Pillow", "pillow")]
)
def test_normalize(test_input, expected):
    # Act
    output = core.normalize(test_input)

    # Assert
    assert output == expected


def test_tabulate_default():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = """\
| python_version | percent | download_count |
| -------------- | ------- | -------------- |
| 2.7            |   51.7% |        342,250 |
| 3.6            |   21.1% |        139,745 |
| 3.5            |   17.2% |        114,254 |
| 3.4            |    7.6% |         50,584 |
| 3.3            |    1.0% |          6,666 |
| 3.7            |    0.7% |          4,516 |
| 2.6            |    0.7% |          4,451 |
| 3.2            |    0.0% |            138 |
| None           |    0.0% |             13 |
"""

    # Act
    tabulated = core.tabulate(rows)

    # Assert
    assert tabulated == expected


def test_tabulate_markdown():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = """\
| python_version | percent | download_count |
| -------------- | ------: | -------------: |
| 2.7            |   51.7% |        342,250 |
| 3.6            |   21.1% |        139,745 |
| 3.5            |   17.2% |        114,254 |
| 3.4            |    7.6% |         50,584 |
| 3.3            |    1.0% |          6,666 |
| 3.7            |    0.7% |          4,516 |
| 2.6            |    0.7% |          4,451 |
| 3.2            |    0.0% |            138 |
| None           |    0.0% |             13 |
"""

    # Act
    tabulated = core.tabulate(rows, markdown=True)

    # Assert
    assert tabulated == expected


def test_validate_date_negative_number():
    # Act
    valid = core.validate_date("-1")

    # Assert
    assert valid


def test_validate_date_positive_number():
    # Act / Assert
    with pytest.raises(ValueError):
        core.validate_date("1")


def test_validate_date_valid_yyyy_mm_dd():
    # Act
    valid = core.validate_date("2018-05-15")

    # Assert
    assert valid


def test_validate_date_invalid_yyyy_mm_dd():
    # Act
    with pytest.raises(ValueError):
        core.validate_date("2018-19-39")


def test_validate_date_other_string():
    # Act / Assert
    with pytest.raises(ValueError):
        core.validate_date("somthing invalid")


def test_format_date_negative_number():
    # Arrange
    dummy_format = "dummy format {}"

    # Act
    date = core.format_date("-1", dummy_format)

    # Assert
    assert date == 'DATE_ADD(CURRENT_TIMESTAMP(), -1, "day")'


def test_format_date_yyy_mm_dd():
    # Act
    date = core.format_date("2018-05-15", core.START_TIMESTAMP)

    # Assert
    assert date == 'TIMESTAMP("2018-05-15 00:00:00")'


def test_month_yyyy_mm():
    # Act
    first, last = core.month_ends("2019-03")

    # Assert
    assert first == "2019-03-01"
    assert last == "2019-03-31"


def test_month_yyyy_mm_dd():
    # Act / Assert
    with pytest.raises(ValueError):
        core.month_ends("2019-03-18")


def test_month_negative_integer():
    # Act / Assert
    with pytest.raises(AttributeError):
        core.month_ends(-30)


def test_normalize_dates_yyy_mm():
    # Arrange
    start_date = "2019-03"
    end_date = "2019-03"

    # Act
    start_date, end_date = core.normalize_dates(start_date, end_date)

    # Assert
    assert start_date == "2019-03-01"
    assert end_date == "2019-03-31"


def test_normalize_dates_yyy_mm_dd_and_negative_integer():
    # Arrange
    start_date = "2019-03-18"
    end_date = -1

    # Act
    start_date, end_date = core.normalize_dates(start_date, end_date)

    # Assert
    assert start_date == "2019-03-18"
    assert end_date == -1


def test_add_percentages():
    # Arrange
    rows = [
        ['python_version', 'download_count'],
        ['2.7', '480056'],
        ['3.6', '328008'],
        ['3.5', '149663'],
        ['3.4', '36837'],
        ['3.7', '1883'],
        ['2.6', '591'],
        ['3.3', '274'],
        ['3.2', '10'],
        ['None', '9'],
        ['3.8', '2'],
    ]

    expected = [
        ['python_version', 'percent', 'download_count'],
        ['2.7', '48.13%', '480056'],
        ['3.6', '32.89%', '328008'],
        ['3.5', '15.01%', '149663'],
        ['3.4', '3.69%', '36837'],
        ['3.7', '0.19%', '1883'],
        ['2.6', '0.06%', '591'],
        ['3.3', '0.03%', '274'],
        ['3.2', '0.00%', '10'],
        ['None', '0.00%', '9'],
        ['3.8', '0.00%', '2'],
    ]

    # Act
    with_percentages = core.add_percentages(rows)

    # Assert
    assert with_percentages == expected


def test_add_total():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = copy.deepcopy(ROWS)
    expected.append(["Total", "", "662617"])

    # Act
    rows_with_total = core.add_download_total(rows)

    # Assert
    assert rows_with_total == expected
