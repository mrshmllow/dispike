import asyncio
import sys
import warnings
from dispike import __version__
from dispike import Dispike

import pytest


def test_import():
    import dispike


def test_initalization():
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    assert (
        isinstance(
            Dispike(
                client_public_key=verification_key.decode(),
                bot_token="BOTTOKEN",
                application_id="APPID",
            ),
            Dispike,
        )
        == True
    )


@pytest.fixture
def dispike_object():
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    return Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )


def test_valid_fastapi_attribute(dispike_object: Dispike):
    from fastapi import FastAPI

    assert isinstance(dispike_object.referenced_application, FastAPI) == True


def test_valid_registrator_object(dispike_object: Dispike):
    from dispike.register.registrator import RegisterCommands

    assert isinstance(dispike_object._registrator, RegisterCommands)
    assert dispike_object._registrator.register == dispike_object.register


def test_valid_event_handler_object(dispike_object: Dispike):
    from dispike.eventer import EventHandler

    assert isinstance(dispike_object.interaction, EventHandler) == True, type(
        dispike_object.interaction
    )


def test_valid_shared_client(dispike_object: Dispike):
    from httpx import Client, URL

    assert isinstance(dispike_object.shared_client, Client) == True, type(
        dispike_object.shared_client
    )
    assert dispike_object.shared_client.base_url == URL(
        f"https://discord.com/api/v8/applications/{dispike_object._application_id}/"
    )


def test_reset_registeration(dispike_object: Dispike):
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    _current_dispike_object = Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )

    assert (
        _current_dispike_object.reset_registration(
            new_bot_token="NewBotToken", new_application_id="newApplicationId"
        )
        == True
    )
    assert (
        _current_dispike_object._registrator.request_headers
        != dispike_object._registrator.request_headers
    )
    assert _current_dispike_object._application_id != dispike_object._application_id


def test_invalid_reset_registration(dispike_object: Dispike):
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    _current_dispike_object = Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )

    with pytest.raises(Exception):
        _current_dispike_object.reset_registration(
            new_bot_token=tuple(0, 0, 0), new_application_id={1: None}
        )


def test_bad_new_command_argument_for_edit_command():
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    _current_dispike_object = Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )

    with pytest.raises(TypeError):
        _current_dispike_object.edit_command(False)


def test_no_guild_id_passed_but_guild_only_argument_for_edit_command():
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    _current_dispike_object = Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )

    with pytest.raises(TypeError):
        _current_dispike_object.edit_command(
            new_command=[], guild_only=True, command_id=1122122
        )


def test_reset_registration_with_none_values(dispike_object: Dispike):
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    _current_dispike_object = Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )

    assert (
        _current_dispike_object.reset_registration(
            new_bot_token=None, new_application_id=None
        )
        == True
    )
    assert _current_dispike_object._bot_token == "BOTTOKEN"
    assert _current_dispike_object._application_id == "APPID"


def test_delete_command_with_invalid_guild_combinations():
    from nacl.encoding import HexEncoder
    from nacl.signing import SigningKey

    _generated_signing_key = SigningKey.generate()
    verification_key = _generated_signing_key.verify_key.encode(encoder=HexEncoder)

    _current_dispike_object = Dispike(
        client_public_key=verification_key.decode(),
        bot_token="BOTTOKEN",
        application_id="APPID",
    )

    with pytest.raises(TypeError):
        _current_dispike_object.delete_command(command_id=123123123123, guild_only=True)


# test exception if no port is set for .run
def test_valid_arguments_for_run_function(dispike_object: Dispike):
    with pytest.raises(ValueError):
        dispike_object.run()

    # test if ValueError is raised if unix_host and port are both set
    with pytest.raises(ValueError):
        dispike_object.run(unix_socket="unix://testingDispikeObject", port=21332)


# def test_display_warning_if_non_local_port(dispike_object: Dispike):
#    with warnings.catch_warnings(record=True) as w:
#        dispike_object.run(port=21332, bind_to_ip_address="0.0.0.0")
#        assert len(w) == 1
#        assert issubclass(w[-1].category, UserWarning)
#        assert "Binding to a IP Address other than 127.0.0.1 may not be secure!" in str(
#            w[-1].message
#        )


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info <= (3, 8), reason="requires python3.8 or higher")
async def test_if_background_function_is_called_correctly(dispike_object: Dispike):
    async def sample_task():
        asyncio.sleep(8888)

    # tbh: i don't know if this is the correct way to test this
    await dispike_object.background(sample_task)
    _running_tasks = [x.get_coro().__name__ for x in list(asyncio.all_tasks())]
    assert "sample_task" in _running_tasks