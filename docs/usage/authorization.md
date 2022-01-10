## Create a new application
In order to use the Factorial API you need a custom Oauth application.

You can manage your applications at the corresponding [dashboard](https://api.factorialhr.com/oauth/applications). You must log in as admin to access this dashboard (in principle).

!!! tip
    If you are creating a new application and are unsure about the settings, use the suggested Redirect URI and check the Confidential box.

!!! success
    Once you have created your application, keep the `client_id`, `client_secret` and `redirect_uri` nearby.

## Authorize your user for using the application 
Before a user can use the application we must grant them authorization.

1. Instantiate the `Factorial` class with a dummy `access_token` (we don't have one).
```
dummy_factorial = Factorial(access_token="abc")
```
2. Call the `authorize` method with the `client_id` and `redirect_uri` that your stored previously. The optional `scope` argument can be `read`, `write` or `read+write` (these values are self-explicatory), and defaults to the latter.
```
dummy_factorial.authorize(
    client_id=client_id,
    redirect_uri=redirect_uri,
)
```
3. The console will show a link.
4. The user must copy this link into a browser.
5. After logging in with their Factorial user, the browser will show an `authorization_key`.

!!! success
    Keep this `authorization_key` nearby.

## Obtain your first access token
Finally we can obtain our first access token.

1. Call the `obtain_access_token` method with the `client_id`, `client_secret` and `redirect_uri` from the first step and the `authorization_key` from the second step.
```
token = dummy_factorial.obtain_access_token(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    authorization_key=authorization_key,
)
```
2. This will return a `Token` object.
!!! warning
    It is super important to store this `token` data in a secure location! Besides the obvious `token.access_token` that we will use to access the API, the attribute `token.refresh_token` will be needed when the token expires.

3. Finally we instantiate the Factorial class with a valid `access_token`.
```
factorial = Factorial(access_token=token.access_token)
```

!!! info
    All tokens have a lifetime of 7 days, afterwards they expire.
!!! tip
    If you call the `obtain_access_token` again, with the same arguments and before the token expires, you will obtain exactly the same token (with the same expiry date).
!!! tip
    You can authorize the same user with different scopes (`read`, `write` or `read+write`), each will need its own access token.

## Refresh your access token
After you token expires you must refresh it.

1. Call the `refresh_access_token` with the `client_id` and `client_secret` from the first step and the `refresh_token` that you stored from the previous step.
```
token = factorial.refresh_access_token(
    client_id=client_id,
    client_secret=client_secret,
    refresh_token=token.refresh_token
)
```
2. This will return a `Token` object.
!!! warning
    Guard this new `token` data in a secure location! It provides a new `token.access_token` and also a new `token.refresh_token` for future refreshments.
