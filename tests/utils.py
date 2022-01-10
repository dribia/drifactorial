"""Utility functions for the testing module.

Dribia 2021, Xavier Hoffmann <xrhoffmann@gmail.com>
"""

import random
import string
from datetime import date, datetime, time
from typing import Any, Dict, Optional

from drifactorial.schemas import Employee


def random_lower_string(*, k: int = 32) -> str:
    """Generate a random string in lowercase."""
    return "".join(random.choices(string.ascii_lowercase, k=k))


def random_int(*, k_min: int = 1, k_max: int = 100000) -> int:
    """Generate a random integer."""
    return random.randint(k_min, k_max)


def random_year(*, year_min: int = 1900, year_max: int = date.today().year) -> int:
    """Generate a random year."""
    return random_int(k_min=year_min, k_max=year_max)


def random_month() -> int:
    """Generate a random month."""
    return random_int(k_min=1, k_max=12)


def random_day_of_year(*, year: int) -> int:
    """Generate a random day of the year."""
    max_days = int(date(year, 12, 31).strftime("%j"))
    return random_int(k_min=1, k_max=max_days)


def random_hour() -> int:
    """Generate a random hour."""
    return random_int(k_min=0, k_max=23)


def random_minute() -> int:
    """Generate a random hour."""
    return random_int(k_min=0, k_max=59)


def random_date_strf() -> str:
    """Generate a random date."""
    year = random_year()
    day_of_year = random_day_of_year(year=year)
    return datetime.strptime(f"{year}-{day_of_year}", "%Y-%j").strftime("%Y-%m-%d")


def random_time_strf() -> str:
    """Generate a random time."""
    hour = random_hour()
    minute = random_minute()
    return f"{str(hour).zfill(2)}:{str(minute).zfill(2)}"


def random_datetime() -> datetime:
    """Generate a random datetime."""
    year = random_year()
    day_of_year = random_day_of_year(year=year)
    dt = datetime.strptime(f"{year}-{day_of_year}", "%Y-%j")
    month = dt.month
    day = dt.day
    hour = random_hour()
    minute = random_minute()
    return datetime(year, month, day, hour, minute)


def random_date() -> date:
    """Generate a random date."""
    dt = random_datetime()
    return date(dt.year, dt.month, dt.day)


def random_selector(random_type):
    """Select a random generator."""
    if random_type is int:
        return random_int()
    if random_type is date:
        return random_date_strf()
    if random_type is time:
        return random_time_strf()
    if random_type is str:
        return random_lower_string()
    if random_type is bool:
        if random.random() < 0.5:
            return True
        else:
            return False
    return None


def random_schema(schema: Any) -> Dict[str, Any]:
    """Generate a random schema object."""
    data = {
        name: random_selector(field.type_) for name, field in schema.__fields__.items()
    }
    return data


def random_employee(
    *, hiring_cents: Optional[int] = None, hiring_type: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a random Employee object."""
    data = random_schema(Employee)
    for name, field in Employee.__fields__.items():
        if field.is_complex():
            data[name] = (random_selector(field.type_),)
    hiring_raw = {
        "base_compensation_amount_in_cents": hiring_cents,
        "base_compensation_type": hiring_type,
    }
    data.update(hiring=hiring_raw)
    return data
