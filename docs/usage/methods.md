!!! info
    Methods regarding authorization and access are described in the [Authorization](https://dribia.github.io/drifactorial/usage/authorization/) page.

!!! tip
    Most methods return custom [pydantic](https://pydantic-docs.helpmanual.io/) objects. See [`schemas.py`](https://github.com/dribia/drifactorial/blob/master/drifactorial/schemas.py) for details.

## get_account
Obtain information about the user's account.

Returns an `Account` object.

## get_employees
Obtain information about **all** employees: previously terminated, currently active and future hirings, from **all** locations.

Returns a list of `Employee` objects.

## get_single_employee
Obtain information about a single employee.

Returns a single `Employee` object.

## get_shifts
Obtain information about **all** shifts: from **all** employees, from **all** times.

Results can be filtered for a specific month with the arguments `year` and `month`. Both arguments must be provided in order
to filter the results. Indicating only the `year` has no filtering effect.

Results can also be filtered for a specific employee with the argument `employee_id`.

Returns a list of `Shift` objects.

## clock_in
Create a new shift for a given `employee_id` with a given clock-in time `now`. 

Returns a single `Shift` object.

!!! warning
    You can't create a new shift if there is still an open shift that hasn't been clocked-out (see [Shift restrictions](https://dribia.github.io/drifactorial/usage/shift_restrictions/) for details).

## clock_out
Update an open shift for a given `employee_id` with a given clock-out time `now`.

Returns a single `Shift` object.

!!! warning
    You can't clock-out a shift that hasn't been clocked-out (see [Shift restrictions](https://dribia.github.io/drifactorial/usage/shift_restrictions/) for details).

## get_leaves
Obtain information about **all** leaves: from **all** employees, from **all** times.

Results can be filtered starting from a specific `start` date and/or ending at a specific `end` date (both dates are included in the filter, see note). 

Results can also be filtered for a specific employee with the argument `employee_id`.

Returns a list of `Leave` objects.

!!! tip
    Leaves that correspond to full days (`half_day=None`) have a `start_on` date and a `finish_on` date.

    Leaves that correspond to half days can be either mornings (`half_day="beggining_of_day"`, note the typo!) or afternoons (`half_day="end_of_day"`).

!!! warning
    When filtering with `start` and/or `end` dates, the filter returns all leaves that have 
    at least one day in the interval. For example, a leave that starts on `01/12/2021` and 
    finishes on `05/12/2021` will be included if we filter with `start=03/12/2021`. 

## get_holidays
Obtain information about **all** company holidays: from **all** locations, from **all** times.

Results can be filtered starting from a specific `start` date and/or ending at a specific `end` date (both dates are included in the filter).

Returns a list of `Holiday` objects.

!!! tip
    All holidays correspond to a single `date`.

    Holidays that correspond to half days can be either mornings (`half_day="beggining_of_day"`, note the typo!) or afternoons (`half_day="end_of_day"`).

## get_daysoff
Obtain information about **all** days off (holidays and leaves) from a given `employee_id`. Only leaves with `approved=True` are included.

Results can be filtered starting from a specific `start` date and/or ending at a specific `end` date (both dates are included in the filter).

Results can also be filtered in order to include weekend days with `include_weekends=True`.

Returns a tuple of 3 objects:

1. A list of `date` objects corresponding to full days off. 
2. A list of `date` objects corresponding to mornings off.
3. A list of `date` objects corresponding to afternoons off.
