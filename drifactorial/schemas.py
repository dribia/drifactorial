"""Data schemes for Factorial API.

Dribia 2021, Xavier Hoffmann <xrhoffmann@gmail.com>
"""

from datetime import date, time
from typing import Optional, Tuple

from pydantic import BaseModel


class Leave(BaseModel):
    """Leave data schema."""

    id: int
    approved: Optional[bool]
    description: Optional[str]
    employee_id: int
    start_on: date
    finish_on: date
    half_day: Optional[str]
    leave_type_id: int
    employee_full_name: str
    leave_type_name: str


class Holiday(BaseModel):
    """Holiday data schema."""

    id: int
    summary: str
    description: Optional[str]
    date: date
    half_day: Optional[str]
    location_id: int


class Hiring(BaseModel):
    """Hiring data schema."""

    base_compensation_amount_in_cents: Optional[int]
    base_compensation_type: Optional[str]


class Employee(BaseModel):
    """Employee data schema."""

    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    company_holiday_ids: Tuple[int, ...]
    location_id: int
    regular_access_starts_on: date
    role: str
    team_ids: Tuple[int, ...]
    timeoff_manager_id: int
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    bank_number: Optional[str]
    birthday_on: Optional[date]
    city: Optional[str]
    country: Optional[str]
    gender: Optional[str]
    hiring: Hiring
    identifier: Optional[str]
    identifier_type: Optional[str]
    manager_id: Optional[int]
    nationality: Optional[str]
    phone_number: Optional[str]
    postal_code: Optional[str]
    social_security_number: Optional[str]
    start_date: Optional[date]
    state: Optional[str]
    terminated_on: Optional[date]


class Shift(BaseModel):
    """Shift data schema."""

    id: int
    day: int
    month: int
    year: int
    clock_in: time
    clock_out: Optional[time]
    employee_id: int
    observations: Optional[str]


class Account(BaseModel):
    """Account data schema."""

    email: str
    full_name: str
    first_name: str
    last_name: str
    employee_id: int
    role: str


class Token(BaseModel):
    """Token data schema."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    created_at: int
