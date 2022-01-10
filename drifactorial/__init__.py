"""Python client for the Factorial API.

Dribia 2021, Xavier Hoffmann <xrhoffmann@gmail.com>
"""


import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from urllib import parse, request

import pydantic
from dateutil.parser import parse as du_parse  # type: ignore

from drifactorial.schemas import Account, Employee, Holiday, Leave, Shift, Token

try:
    from importlib.metadata import version  # type: ignore
except ModuleNotFoundError:
    from importlib_metadata import version  # type: ignore

__version__ = version(__name__)


URL_BASE = "https://api.factorialhr.com"
URL_API = "api/v1"
URL_LEAVES = "leaves"
URL_HOLIDAYS = "company_holidays"
URL_EMPLOYEES = "employees"
URL_SHIFTS = "shifts"
URL_ACCOUNT = "me"
URL_CLOCK_IN = "clock_in"
URL_CLOCK_OUT = "clock_out"
URL_OAUTH = "oauth"
URL_AUTHORIZE = "authorize"
URL_TOKEN = "token"
SCOPES = ["read", "write", "read+write"]
DEFAULT_SCOPE = "read+write"
HALF_DAY_AM = "beggining_of_day"
HALF_DAY_PM = "end_of_day"


def _parse_date(start: Any) -> date:
    """Aux function to parse date."""
    parsed = start if isinstance(start, date) else du_parse(start).date()
    return parsed


def daterange(
    start: date, end: date, *, include_end: bool = True
) -> Generator[date, None, None]:
    """Generate range of dates.

    Args:
        start: Start date of range.
        end: End date of range.
        include_end: Optional, include end date (True) or not (False).

    Yields:
        Date object.
    """
    n_days = (end - start).days
    if include_end:
        n_days += 1
    for n in range(n_days):
        yield start + timedelta(n)


class Factorial:
    """Python client for Factorial API."""

    def __init__(self, *, access_token: str):
        """Instantiate client."""
        self.access_token = access_token

    def _get(
        self, *, endpoint: str, params: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Generic GET method.

        Args:
            endpoint: Endpoint of the API to request.
            params: Optional request parameters.

        Returns:
            Response of the GET request in JSON format.
        """
        url = f"{URL_BASE}/{URL_API}/{endpoint}"
        if params is not None:
            url = f"{url}?{parse.urlencode(params)}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        request_url = request.Request(url, headers=headers)
        response = request.urlopen(request_url)
        return json.loads(response.read())

    def _post(self, *, endpoint: str, payload: Dict[str, str]) -> Dict[str, Any]:
        """Generic POST method.

        Args:
            endpoint: Endpoint of the API to request.
            payload: Data to post during request.

        Returns:
            Response of the POST request in JSON format.
        """
        url = f"{URL_BASE}/{URL_API}/{endpoint}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        data = json.dumps(payload).encode("utf-8")
        request_url = request.Request(url, data=data, headers=headers)
        response = request.urlopen(request_url)
        return json.loads(response.read())

    def get_holidays(
        self, *, start: Optional[date] = None, end: Optional[date] = None
    ) -> List[Holiday]:
        """Get company holidays information.

        Args:
            start: Optional, start date of filter (included).
            end: Optional, end date of filter (included).

        Returns:
            List of Holiday objects.
        """
        response = self._get(endpoint=URL_HOLIDAYS)
        parsed = [pydantic.parse_obj_as(Holiday, x) for x in response]
        if start is not None:
            parsed = [x for x in parsed if x.date >= _parse_date(start)]
        if end is not None:
            parsed = [x for x in parsed if x.date <= _parse_date(end)]
        return parsed

    def get_employees(self) -> List[Employee]:
        """Get employees information."""
        response = self._get(endpoint=URL_EMPLOYEES)
        return [pydantic.parse_obj_as(Employee, x) for x in response]

    def get_single_employee(self, *, employee_id: int) -> Employee:
        """Get single employee information."""
        response = self._get(endpoint=f"{URL_EMPLOYEES}/{employee_id}")
        return pydantic.parse_obj_as(Employee, response)

    def get_shifts(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        employee_id: Optional[int] = None,
    ) -> List[Shift]:
        """Get shifts information.

        Arguments `year` and `month` must both be given in order to
          filter shifts based on dates. If one of the two is missing,
          all shifts will be returned (without filtering).

        Args:
            year: Optional, year to filter.
            month: Optional, month to filter.
            employee_id: Optional, filter on employee id.

        Returns:
            List of Shift objects.
        """
        params = {}
        if year is not None and month is not None:
            params = {"year": f"{year}", "month": f"{month}"}
        response = self._get(endpoint=URL_SHIFTS, params=params)
        parsed = [pydantic.parse_obj_as(Shift, x) for x in response]
        if employee_id is not None:
            parsed = [x for x in parsed if x.employee_id == employee_id]
        return parsed

    def get_leaves(
        self,
        *,
        start: Optional[date] = None,
        end: Optional[date] = None,
        employee_id: Optional[int] = None,
    ) -> List[Leave]:
        """Get leaves information.

        Args:
            start: Optional, start date of filter (included).
            end: Optional, end date of filter (included).
            employee_id: Optional, filter on employee id.

        Returns:
            List of Leaves objects.
        """
        response = self._get(endpoint=URL_LEAVES)
        parsed = [pydantic.parse_obj_as(Leave, x) for x in response]
        if start is not None:
            parsed = [x for x in parsed if x.finish_on >= _parse_date(start)]
        if end is not None:
            parsed = [x for x in parsed if x.start_on <= _parse_date(end)]
        if employee_id is not None:
            parsed = [x for x in parsed if x.employee_id == employee_id]
        return parsed

    def get_daysoff(
        self,
        *,
        employee_id: int,
        start: Optional[date] = None,
        end: Optional[date] = None,
        include_weekend: bool = False,
    ) -> Tuple[List[date], List[date], List[date]]:
        """Get days off (holidays and leaves) for a single employee.

        Redefines date filter with employee start and termination date.
        Filters holidays by employee location.
        Filters only approved leaves.
        Separates full, morning and afternoon days off.

        Args:
            employee_id: Employee id.
            start: Optional, start date of filter (included).
            end: Optional, end date of filter (included).
            include_weekend: Optional, include weekend days (True) or
              not (False).

        Returns:
            List of full days off.
            List of morning days off.
            List of afternoon days off.
        """
        # get employee information
        employee = self.get_single_employee(employee_id=employee_id)

        # find valid start
        if employee.start_date is None:
            aux_start = date.today()
        else:
            aux_start = employee.start_date
        if start is not None:
            aux_start = max(aux_start, _parse_date(start))

        # find valid end
        if employee.terminated_on is None:
            aux_end = date.today()
        else:
            aux_end = employee.terminated_on
        if end is not None:
            aux_end = min(aux_end, _parse_date(end))

        # get holidays for this employee
        holidays = [
            x
            for x in self.get_holidays(start=aux_start, end=aux_end)
            if x.id in employee.company_holiday_ids
        ]

        # get leaves for this employee
        leaves = [
            x
            for x in self.get_leaves(
                start=aux_start, end=aux_end, employee_id=employee_id
            )
            if x.approved
        ]

        # extract holidays: full days, mornings, afternoons
        days_full = [x.date for x in holidays if x.half_day is None]
        days_am = [x.date for x in holidays if x.half_day == HALF_DAY_AM]
        days_pm = [x.date for x in holidays if x.half_day == HALF_DAY_PM]

        # extract leaves
        days_full = days_full[:] + [
            y
            for x in leaves
            for y in daterange(max(x.start_on, aux_start), min(x.finish_on, aux_end))
            if x.half_day is None
        ]
        days_am = days_am[:] + [x.start_on for x in leaves if x.half_day == HALF_DAY_AM]
        days_pm = days_pm[:] + [x.start_on for x in leaves if x.half_day == HALF_DAY_PM]

        # remove weekends
        if not include_weekend:
            days_full = [x for x in days_full if x.weekday() < 5]
            days_am = [x for x in days_am if x.weekday() < 5]
            days_pm = [x for x in days_pm if x.weekday() < 5]

        return sorted(days_full), sorted(days_am), sorted(days_pm)

    def get_account(self) -> Account:
        """Get account information."""
        response = self._get(endpoint=URL_ACCOUNT)
        return pydantic.parse_obj_as(Account, response)

    def clock_in(self, *, now: datetime, employee_id: int) -> Shift:
        """Post clock-in time."""
        payload = {"now": f"{now.isoformat()}", "employee_id": f"{employee_id}"}
        response = self._post(endpoint=f"{URL_SHIFTS}/{URL_CLOCK_IN}", payload=payload)
        return pydantic.parse_obj_as(Shift, response)

    def clock_out(self, *, now: datetime, employee_id: int) -> Shift:
        """Post clock-out time."""
        payload = {"now": f"{now.isoformat()}", "employee_id": f"{employee_id}"}
        response = self._post(endpoint=f"{URL_SHIFTS}/{URL_CLOCK_OUT}", payload=payload)
        return pydantic.parse_obj_as(Shift, response)

    @staticmethod
    def authorize(
        *, client_id: str, redirect_uri: str, scope: str = DEFAULT_SCOPE
    ) -> None:
        """Obtain authorization link."""
        if scope not in SCOPES:
            raise ValueError(f"Invalid scope. Options are: {', '.join(SCOPES)}.")
        auth_url = [
            f"{URL_BASE}/{URL_OAUTH}/{URL_AUTHORIZE}?client_id={client_id}",
            f"redirect_uri={redirect_uri}",
            "response_type=code",
            f"scope={scope}",
        ]
        text = [
            "Authorization required.",
            "Follow this link and store your authorization key:",
        ]
        print(" ".join(text))
        print("&".join(auth_url))
        return None

    @staticmethod
    def _post_token(*, data: Dict[str, str]) -> Dict[str, Any]:
        """Request access token.

        Args:
            data: Settings and credentials needed to obtain the token.

        Returns:
            Response of the POST request.

        Raise:
            ResponseError: If the response raises an issue.
        """
        url = f"{URL_BASE}/{URL_OAUTH}/{URL_TOKEN}"
        data_parsed = parse.urlencode(data).encode()
        request_url = request.Request(url, data=data_parsed)
        response = request.urlopen(request_url)
        return json.loads(response.read())

    def obtain_access_token(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        authorization_key: str,
    ) -> Token:
        """Obtain access token from authorization key."""
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": authorization_key,
            "grant_type": "authorization_code",
        }
        response = self._post_token(data=data)
        token = pydantic.parse_obj_as(Token, response)
        self.access_token = token.access_token
        return token

    def refresh_access_token(
        self, *, client_id: str, client_secret: str, refresh_token: str
    ) -> Token:
        """Refresh access token when expired."""
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = self._post_token(data=data)
        token = pydantic.parse_obj_as(Token, response)
        self.access_token = token.access_token
        return token
