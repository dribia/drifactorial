<p style="text-align: center; padding-bottom: 1rem;">
    <a href="https://dribia.github.io/drifactorial">
        <img 
            src="https://dribia.github.io/drifactorial/img/logo_dribia_blau_cropped.png" 
            alt="drifactorial" 
            style="display: block; margin-left: auto; margin-right: auto; width: 40%;"
        >
    </a>
</p>

<p style="text-align: center">
    <a href="https://github.com/dribia/drifactorial/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/dribia/drifactorial/workflows/Test/badge.svg" alt="Test">
    </a>
    <a href="https://github.com/dribia/drifactorial/actions?query=workflow%3APublish" target="_blank">
        <img src="https://github.com/dribia/drifactorial/workflows/Publish/badge.svg" alt="Publish">
    </a>
    <a href="https://codecov.io/gh/dribia/drifactorial" target="_blank">
        <img src="https://img.shields.io/codecov/c/github/dribia/drifactorial?color=%2334D058" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/drifactorial" target="_blank">
        <img src="https://img.shields.io/pypi/v/drifactorial?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
</p>

<p style="text-align: center;">
    <em>Python client for the Factorial API.</em>
</p>



---

**Documentation**: <a href="https://dribia.github.io/drifactorial" target="_blank">https://dribia.github.io/drifactorial</a>

**Source Code**: <a href="https://github.com/dribia/drifactorial" target="_blank">https://github.com/dribia/drifactorial</a>

---

[Factorial](https://factorialhr.com/) is a software dedicated to manage everything related to HR.

**Drifactorial** provides a tiny Python interface to the official API.

## Key features

* **Authorize programatic access** to your application.
* Obtain and refresh **access tokens**.
* Implements **generic GET and POST** methods.
* Parses responses to **Pydantic models**.
* Easily implement **additional methods**.

## Example

The simplest example.

```python
from drifactorial import Factorial
from datetime import datetime

factorial = Factorial(access_token="abc")

# get list of employees
employees = factorial.get_employees()
# get list of company holidays
holidays = factorial.get_holidays()
# get list of leaves
leaves = factorial.get_leaves()
# get list of days off of an employee
daysoff = factorial.get_daysoff(employee_id=123)
# get list of all shifts in October 2021
shifts = factorial.get_shifts(year=2021, month=10)
# get single employee
single_employee = factorial.get_single_employee(employee_id=123)
# get my account
account = factorial.get_account()

# clock in shift
clock_in = datetime(2021, 10, 1, 9, 0)
new_shift = factorial.clock_in(now=clock_in, employee_id=123)
# clock out shift
clock_out = datetime(2021, 10, 1, 13, 0)
updated_shift = factorial.clock_out(now=clock_in, employee_id=123)
```
