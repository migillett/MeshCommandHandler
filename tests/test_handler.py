import pytest

from meshcommandhandler import MeshCommandHandler


@pytest.fixture
def handler() -> MeshCommandHandler:
    return MeshCommandHandler(version="testing")


def test_info(handler: MeshCommandHandler) -> None:
    # commands should have spaces stripped, check both
    for m in ["!i", " !i ", "!I"]:
        response = handler.handle(m, sender_id="test")
        assert response.message.startswith("vtesting")


def test_help(handler: MeshCommandHandler) -> None:
    response = handler.handle("!h", sender_id="test")
    assert (
        response.message
        == """!w: Get/Set waypoints
!cmd: run CLI commands
!i: Pkg info
!h: Help menu"""
    )


def test_no_command(handler: MeshCommandHandler) -> None:
    # Bad command that has no response
    response = handler.handle("!hello", sender_id="test")
    assert response is None


def test_test_message(handler: MeshCommandHandler) -> None:
    msg = "test"
    resp = handler.handle(msg, sender_id="test ")
    assert resp.message == "Test received: test"


def test_waypoints(handler: MeshCommandHandler) -> None:
    # invalid input. must be 0.0,0.0
    resp = handler.handle("!w 0.000, 0.000", "test")
    assert resp.message == "Invalid input"

    # not a float
    resp = handler.handle("!w 33.7449682,notafloat", "test")
    assert resp.message == "Invalid input"

    # out of bounds
    resp = handler.handle("!w 100.00,-200.00", "test")
    assert resp.message == "Invalid input"

    # missing ','
    resp = handler.handle("!w 33.7449682", "test")
    assert resp.message == "Invalid input"

    # happy path
    resp = handler.handle("!w 33.74496821234,-84.38990781234", "test")
    assert resp.message == "Waypoint accepted"
    resp = handler.handle("!w", "test")
    # round to 6 decimal places
    assert resp.message == "33.744968,-84.389908"


def test_commands(handler: MeshCommandHandler) -> None:
    handler._load_commands("tests/filenothere.json")
    assert handler._commands == {}

    handler._load_commands("tests/test_cmds.json")
    assert handler._commands == {"cmd1": "test command", "cmd2": "test2"}

    resp = handler.handle("!cmd cmd1", "not admin")
    assert resp.message == "Admin nodes not defined"

    handler._admins = ["admin"]
    resp = handler.handle("!cmd cmd1", "not admin")
    assert resp.message == "Unauthorized"
    resp = handler.handle("!cmd list", "admin")
    assert resp.message == "cmd1,cmd2"
    resp = handler.handle("!cmd cmd1", "admin")
    assert resp.message == "Command executing..."
