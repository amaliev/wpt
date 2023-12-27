
import pytest
import webdriver.bidi.error as error

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    "parameters",
    [
        #{ "descriptor": { "name": "geolocation" }, "state": "granted" }
        {
            "descriptor": {
                "name": 23
            },
            "state": "granted"
        },
        {
            "descriptor": {},
            "state": "granted"
        },
        {
            "descriptor": {
                "name": "geolocation"
            },
            "state": "Granted"
        },
        {
            "descriptor": 23,
            "state": "granted"
        },
        {
            "descriptor": "geolocation",
            "state": "granted"
        },
        {
            "descriptor": [{
                "name": "geolocation"
            }],
            "state": "granted"
        },
    ])
async def test_invalid_parameters(bidi_session, new_tab, url, parameters):
    test_url = url("/common/blank.html", protocol="https")
    await bidi_session.browsing_context.navigate(
        context=new_tab["context"],
        url=test_url,
        wait="complete",
    )
    with pytest.raises(error.InvalidArgumentException):
      await bidi_session.permissions.set_permission(descriptor=parameters['descriptor'], state=parameters['state'])