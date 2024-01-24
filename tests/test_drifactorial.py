"""Test module for the drifactorial package.

Dribia 2021, Xavier Hoffmann <xrhoffmann@gmail.com>
"""

import json
import re
from datetime import date, datetime, time, timedelta
from io import StringIO
from typing import List, Optional

import pytest
from pydantic import TypeAdapter
from pytest import CaptureFixture
from pytest_mock import MockerFixture

import drifactorial
from drifactorial import Factorial
from drifactorial.schemas import Account, Employee, Hiring, Holiday, Leave, Shift, Token
from tests import utils


def test_version():
    """Assert that `__version__` exists and is valid."""
    assert re.match(r"\d.\d.\d", drifactorial.__version__)


def test_daterange():
    """Asser daterange generator."""
    # case invalid range
    start = date(2021, 2, 1)
    end = date(2021, 1, 1)
    dates = list(drifactorial.daterange(start, end))
    assert len(dates) == 0
    # case include end
    end = date(2021, 2, 28)
    dates = list(drifactorial.daterange(start, end))
    assert len(dates) == 28
    # case exclude end
    dates = list(drifactorial.daterange(start, end, include_end=False))
    assert len(dates) == 27


def test_get_holidays(mocker: MockerFixture):
    """Assert get holidays method."""
    fake_response_holidays = [utils.random_schema(Holiday)]
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_holidays)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    holidays = factorial.get_holidays()

    # prep parsing
    date_fields = [
        name for name, field in Holiday.model_fields.items() if field.annotation is date
    ]

    # make assertions
    assert hasattr(holidays, "__len__")
    assert len(holidays) == 1
    for field, value in fake_response_holidays[0].items():
        if field in date_fields:
            dt = datetime.strptime(value, "%Y-%m-%d")
            d = date(dt.year, dt.month, dt.day)
            assert getattr(holidays[0], field) == d
        else:
            assert getattr(holidays[0], field) == value

    fake_date = TypeAdapter(date).validate_python(fake_response_holidays[0]["date"])
    # test filter start
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_holidays)),
    )
    holidays = factorial.get_holidays(start=fake_date + timedelta(-1))
    assert len(holidays) == 1
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_holidays)),
    )
    holidays = factorial.get_holidays(start=fake_date + timedelta(1))
    assert len(holidays) == 0
    # test filter end
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_holidays)),
    )
    holidays = factorial.get_holidays(end=fake_date + timedelta(1))
    assert len(holidays) == 1
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_holidays)),
    )
    holidays = factorial.get_holidays(end=fake_date + timedelta(-1))
    assert len(holidays) == 0


def test_get_leaves(mocker: MockerFixture):
    """Assert get leaves method."""
    fake_response_leaves = [utils.random_schema(Leave)]
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    leaves = factorial.get_leaves()

    # prep parsing
    date_fields = [
        name for name, field in Leave.model_fields.items() if field.annotation is date
    ]

    # make assertions
    assert hasattr(leaves, "__len__")
    assert len(leaves) == 1
    for field, value in fake_response_leaves[0].items():
        if field in date_fields:
            dt = datetime.strptime(value, "%Y-%m-%d")
            d = date(dt.year, dt.month, dt.day)
            assert getattr(leaves[0], field) == d
        else:
            assert getattr(leaves[0], field) == value

    # test filter employee
    employee_id = fake_response_leaves[0]["employee_id"]
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    leaves = factorial.get_leaves(employee_id=employee_id)
    assert len(leaves) == 1
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    leaves = factorial.get_leaves(employee_id=employee_id + 1)
    assert len(leaves) == 0

    # test filter start
    fake_date = TypeAdapter(date).validate_python(fake_response_leaves[0]["finish_on"])
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    leaves = factorial.get_leaves(start=fake_date + timedelta(1))
    assert len(leaves) == 0
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    leaves = factorial.get_leaves(start=fake_date + timedelta(-1))
    assert len(leaves) == 1

    # test filter end
    fake_date = TypeAdapter(date).validate_python(fake_response_leaves[0]["start_on"])
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    leaves = factorial.get_leaves(end=fake_date + timedelta(1))
    assert len(leaves) == 1
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_leaves)),
    )
    leaves = factorial.get_leaves(end=fake_date + timedelta(-1))
    assert len(leaves) == 0


@pytest.mark.parametrize("hiring_cents", [None, utils.random_int()])
@pytest.mark.parametrize("hiring_type", [None, utils.random_lower_string()])
def test_get_employees(mocker: MockerFixture, hiring_cents: int, hiring_type: str):
    """Assert get employees method."""
    fake_response_employees = [
        utils.random_employee(hiring_cents=hiring_cents, hiring_type=hiring_type)
    ]
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_employees)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    employees = factorial.get_employees()

    # prep parsing
    hiring_parsed = Hiring(
        base_compensation_amount_in_cents=hiring_cents,
        base_compensation_type=hiring_type,
    )
    fake_response_employees[0].update(hiring=hiring_parsed)
    date_fields = [
        name
        for name, field in Employee.model_fields.items()
        if field.annotation is date
    ]

    # make assertions
    assert hasattr(employees, "__len__")
    assert len(employees) == 1
    for field, value in fake_response_employees[0].items():  # type: ignore
        if field in date_fields:
            dt = datetime.strptime(value, "%Y-%m-%d")
            d = date(dt.year, dt.month, dt.day)
            assert getattr(employees[0], field) == d  # type: ignore
        else:
            assert getattr(employees[0], field) == value  # type: ignore


@pytest.mark.parametrize("year", [None, utils.random_year()])
@pytest.mark.parametrize("month", [None, utils.random_month()])
def test_get_shifts(
    mocker: MockerFixture,
    year: Optional[int],
    month: Optional[int],
):
    """Assert get shifts method."""
    fake_response_shifts = [utils.random_schema(Shift)]
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_shifts)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    shifts = factorial.get_shifts(year=year, month=month)

    # prep parsing
    date_fields = [
        name for name, field in Shift.model_fields.items() if field.annotation is date
    ]
    time_fields = [
        name for name, field in Shift.model_fields.items() if field.annotation is time
    ]

    # make assertions
    assert hasattr(shifts, "__len__")
    assert len(shifts) == 1
    for field, value in fake_response_shifts[0].items():
        if field in date_fields:
            dt = datetime.strptime(value, "%Y-%m-%d")
            d = date(dt.year, dt.month, dt.day)
            assert getattr(shifts[0], field) == d
        elif field in time_fields:
            dt = datetime.strptime(value, "%H:%M")
            t = time(dt.hour, dt.minute)
            assert getattr(shifts[0], field) == t
        else:
            assert getattr(shifts[0], field) == value

    # test filter employee
    employee_id = fake_response_shifts[0]["employee_id"]
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_shifts)),
    )
    shifts = factorial.get_shifts(employee_id=employee_id)
    assert len(shifts) == 1
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_shifts)),
    )
    shifts = factorial.get_shifts(employee_id=employee_id + 1)
    assert len(shifts) == 0


def test_get_account(mocker: MockerFixture):
    """Assert get account method."""
    fake_response_account = utils.random_schema(Account)
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_account)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    account = factorial.get_account()

    # make assertions
    assert not hasattr(account, "__len__")
    for field, value in fake_response_account.items():
        assert getattr(account, field) == value


@pytest.mark.parametrize("hiring_cents", [None, utils.random_int()])
@pytest.mark.parametrize("hiring_type", [None, utils.random_lower_string()])
def test_get_single_employee(
    mocker: MockerFixture, hiring_cents: int, hiring_type: str
):
    """Assert get single employee method."""
    fake_response_single_employee = utils.random_employee(
        hiring_cents=hiring_cents, hiring_type=hiring_type
    )
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_single_employee)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    single_employee = factorial.get_single_employee(employee_id=utils.random_int())

    # prep parsing
    hiring_parsed = Hiring(
        base_compensation_amount_in_cents=hiring_cents,
        base_compensation_type=hiring_type,
    )
    fake_response_single_employee.update(hiring=hiring_parsed)
    date_fields = [
        name
        for name, field in Employee.model_fields.items()
        if field.annotation is date
    ]

    # make assertions
    assert not hasattr(single_employee, "__len__")
    for field, value in fake_response_single_employee.items():  # type: ignore
        if field in date_fields:
            dt = datetime.strptime(value, "%Y-%m-%d")
            d = date(dt.year, dt.month, dt.day)
            assert getattr(single_employee, field) == d  # type: ignore
        else:
            assert getattr(single_employee, field) == value  # type: ignore


def test_clock_in(mocker: MockerFixture):
    """Assert clock in method."""
    fake_response_clock_in = utils.random_schema(Shift)
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_clock_in)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    shift = factorial.clock_in(
        now=utils.random_datetime(), employee_id=utils.random_int()
    )

    # prep parsing
    time_fields = [
        name for name, field in Shift.model_fields.items() if field.annotation is time
    ]

    # make assertions
    assert not hasattr(shift, "__len__")
    for field, value in fake_response_clock_in.items():
        if field in time_fields:
            dt = datetime.strptime(value, "%H:%M")
            t = time(dt.hour, dt.minute)
            assert getattr(shift, field) == t
        else:
            assert getattr(shift, field) == value


def test_clock_out(mocker: MockerFixture):
    """Assert clock out method."""
    fake_response_clock_in = utils.random_schema(Shift)
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_clock_in)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    shift = factorial.clock_out(
        now=utils.random_datetime(), employee_id=utils.random_int()
    )

    # prep parsing
    time_fields = [
        name for name, field in Shift.model_fields.items() if field.annotation is time
    ]

    # make assertions
    assert not hasattr(shift, "__len__")
    for field, value in fake_response_clock_in.items():
        if field in time_fields:
            dt = datetime.strptime(value, "%H:%M")
            t = time(dt.hour, dt.minute)
            assert getattr(shift, field) == t
        else:
            assert getattr(shift, field) == value


def test_authorize(capsys: CaptureFixture):
    """Assert authorize method."""
    factorial = Factorial(access_token=utils.random_lower_string())
    auth_link = factorial.obtain_authorization_link(
        client_id=utils.random_lower_string(), redirect_uri=utils.random_lower_string()
    )
    assert auth_link.startswith("https://")
    params = auth_link.split("&")
    assert len(params) == 4
    for param in ["client_id", "redirect_uri", "response_type", "scope"]:
        assert param in auth_link

    factorial.authorize(
        client_id=utils.random_lower_string(), redirect_uri=utils.random_lower_string()
    )
    captured = capsys.readouterr()
    text = captured.out.split("\n")
    assert text[0].startswith("Authorization required.")
    assert text[0].endswith(":")
    line = text[1].split("?")
    assert line[0].startswith("https://")
    params = line[1].split("&")
    assert len(params) == 4
    for param in ["client_id", "redirect_uri", "response_type", "scope"]:
        assert param in line[1]


def test_obtain_access_token(mocker: MockerFixture):
    """Assert obtain acces token method."""
    fake_response_obtain_token = utils.random_schema(Token)
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_obtain_token)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    token = factorial.obtain_access_token(
        client_id=utils.random_lower_string(),
        client_secret=utils.random_lower_string(),
        redirect_uri=utils.random_lower_string(),
        authorization_key=utils.random_lower_string(),
    )
    assert not hasattr(token, "__len__")
    for field, value in fake_response_obtain_token.items():
        assert getattr(token, field) == value


def test_refresh_access_token(mocker: MockerFixture):
    """Assert obtain acces token method."""
    fake_response_obtain_token = utils.random_schema(Token)
    mocker.patch(
        "drifactorial.request.urlopen",
        return_value=StringIO(json.dumps(fake_response_obtain_token)),
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    token = factorial.refresh_access_token(
        client_id=utils.random_lower_string(),
        client_secret=utils.random_lower_string(),
        refresh_token=utils.random_lower_string(),
    )
    assert not hasattr(token, "__len__")
    for field, value in fake_response_obtain_token.items():
        assert getattr(token, field) == value


def test_get_daysoff(mocker: MockerFixture):
    """Assert get daysoff method."""
    # test filter holidays on employee id successful
    employee = TypeAdapter(Employee).validate_python(utils.random_employee())
    holidays = [
        TypeAdapter(Holiday).validate_python(utils.random_schema(Holiday))
        for i in range(3)
    ]
    holidays[0].half_day = None
    holidays[1].half_day = drifactorial.HALF_DAY_AM
    holidays[2].half_day = drifactorial.HALF_DAY_PM
    employee.start_date = min(x.date for x in holidays) + timedelta(-1)
    employee.terminated_on = None
    employee.company_holiday_ids = tuple(x.id for x in holidays)
    leaves_empty: List = []
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves_empty,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 1

    # test filter holidays on employee id unsuccessful
    employee.company_holiday_ids = tuple(x.id + 1 for x in holidays)
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves_empty,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0

    # test filter weekends included
    # using the same employee and holidays
    weekend_day = date(2021, 12, 25)
    for i in range(3):
        holidays[i].date = weekend_day
    employee.company_holiday_ids = tuple(x.id for x in holidays)
    employee.start_date = min(x.date for x in holidays) + timedelta(-1)
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves_empty,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 1

    # test filter weekends excluded
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves_empty,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=False)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0

    # test filter approved leaves successful
    # using the same employee
    holidays_empty: List = []
    leaves = [
        TypeAdapter(Leave).validate_python(utils.random_schema(Leave)) for _ in range(3)
    ]
    leaves[0].half_day = None
    leaves[1].half_day = drifactorial.HALF_DAY_AM
    leaves[2].half_day = drifactorial.HALF_DAY_PM
    for i in range(3):
        leaves[i].approved = True
        leaves[i].finish_on = leaves[i].start_on
    leaves[0].finish_on = leaves[0].start_on + timedelta(1)
    employee.start_date = min(x.start_on for x in leaves) + timedelta(-1)
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    assert len(daysoff[0]) == 2
    assert len(daysoff[1]) == 1
    assert len(daysoff[2]) == 1

    # test filter approved leaves unsuccessful
    for i in range(3):
        leaves[i].approved = False
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0

    # test time logic
    # using same employee, only leaves[0]
    leaves = leaves[:1]
    leaves[0].approved = True
    min_date = leaves[0].start_on
    max_date = leaves[0].finish_on

    # standard behavior, should not fail
    employee.start_date = min_date + timedelta(-1)
    employee.terminated_on = None
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    assert len(daysoff[0]) == 2
    assert len(daysoff[1]) == 0
    assert len(daysoff[2]) == 0

    # overwrite start date, should fail
    start = max_date + timedelta(1)
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(
        employee_id=employee.id, include_weekend=True, start=start
    )
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0

    # overwrite end date, should fail
    end = min_date + timedelta(-1)
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(
        employee_id=employee.id, include_weekend=True, end=end
    )
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0

    # termination date before leaves
    employee.start_date = None
    employee.terminated_on = min_date + timedelta(-1)
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0

    #  termination date after leaves
    employee.start_date = max_date + timedelta(1)
    employee.terminated_on = None
    mocker.patch(
        "drifactorial.Factorial.get_single_employee",
        return_value=employee,
    )
    mocker.patch(
        "drifactorial.Factorial.get_leaves",
        return_value=leaves,
    )
    mocker.patch(
        "drifactorial.Factorial.get_holidays",
        return_value=holidays_empty,
    )
    factorial = Factorial(access_token=utils.random_lower_string())
    daysoff = factorial.get_daysoff(employee_id=employee.id, include_weekend=True)
    assert len(daysoff) == 3
    for el in daysoff:
        assert len(el) == 0
