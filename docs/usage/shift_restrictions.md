The Factorial API is supposed to restrict creating new shifts if the previous one is still open or updating shifts that don't exist. However, it is buggy and presents some unexpected behavior.

!!! danger
    The API may be slow in responding when clocking in and out. It is recommended to add a generous time-out.

## Clocking in

!!! question "Expected behavior"
    You can't create a new shift if the previous shift still open.

Imagine you clock-in a shift on `01/12/2021` at `09:00`. In principle (the API has shown some bugs...) 
you must first clock-out this shift, say at `13:00`. Afterwards you will be able to clock-in new shifts.

Now consider the scenario where we follow the previous step clocking in a shift on `30/11/2021`
at `09:00`. We would expect that we must first close this shift before being able to create a 
new one.

However, given that there exists a **later closed shift** we are able to clock-in a 
new shift (for example, on `02/12/2021` at `09:00`) even if the shift from `30/11/2021` is still open.  

## Clocking out

!!! question "Expected behavior"
    You can't clock-out a shift that hasn't been clocked-in.

This is true, however care should be taken if clock-out on a different date.

Image you clock-in on `01/12/2021` at `09:00`. Afterwards you clock-out on `02/12/2021`
at `19:00`. This will cause the shift of `01/12/2021` to be clocked-out at `23:59` and it will create
a new shift on `02/12/2021` with clock-in time `00:00` and clock-out time `19:00`. Beware that
the `clock_out` method will return a single `Shift` object, corresponding to the date that you have provided.

Also, you can only clock-out **the most recent open shift**. In the buggy example that we
discussed in the [Clocking in](https://dribia.github.io/drifactorial/usage/shift_restrictions/#clocking-in) section, we will never be able to
*programmatically* clock-out the shift from `30/11/2021` that has remained open. The user will have to update
it manually using the web interface.
