import inspect
import logging
from json import load
from os import path

from meshcommandhandler import __version__

from .models import Coordinates, UserResponse

logger = logging.getLogger(__name__)


class MeshCommandHandler:
    def __init__(
        self,
        command_prefix: str = "!",
        admins: list[str] | None = None,
        commands_json: str | None = None,
    ) -> None:

        self._prefix = command_prefix
        self._admins = admins
        self._version = __version__
        self._url = "https://github.com/migillett/MeshCommandHandler"
        logger.info(f"Message Handler v{self._version} Initialized")

        self._coordinates: Coordinates | None = None
        self._commands: dict = {}
        self._load_commands(json_path=commands_json)

    def _load_commands(self, json_path: str | None = None) -> None:
        if json_path is not None and path.exists(json_path):
            with open(path.join(json_path), "r") as json_file:
                self._commands = load(json_file)
                logger.info(f"Loaded commands: {self._commands}")
        else:
            logger.info("Unable to load commands JSON file")

    def _prepare_message(self, message: str) -> list[str]:
        msg = message.strip()
        return [w.lower() for w in msg.split(" ")]

    def _rejoin_msg(self, message_list: list[str]) -> str:
        return " ".join(message_list).strip()

    def _is_test(self, msg: list[str]) -> bool:
        return len(msg) > 0 and msg[0] in ["test", "testing", "ping"]

    # def _cmd_config(self, user_id: str) -> str:
    #     """1 - !c: Current config

    #     Returns the current running configuration
    #     """
    #     resp = UserResponse(
    #         message="TODO", user_id=user_id
    #     )
    #     return resp

    def _cmd_waypoints(self, msg: list[str], user_id: str) -> list:
        """2 - !w: Get/Set waypoints

        Allows user to submit or request waypoints from the server

        Currently only supporting 1 waypoint at a time, but want to add `list[Coordinates]`

        `!w` return waypoints

        `!w latitude,longitude` adds a waypoint
        """
        if len(msg) > 2:
            return UserResponse(message="Invalid input", user_id=user_id)

        elif len(msg) == 1:
            return UserResponse(
                message=self._coordinates.to_message(),
                user_id=user_id,
            )

        try:
            c = msg[1].split(",")
            self._coordinates = Coordinates(latitude=c[0], longitude=c[1])
            logger.info(f"Received coordinates: {self._coordinates}")
            return UserResponse(message="Waypoint accepted", user_id=user_id)

        except (ValueError, IndexError):
            logger.warning(f"Unable to conform message to coords: {msg}")
            return UserResponse(message="Invalid input", user_id=user_id)

    def _cmd_run_command(self, msg: list[str], user_id: str) -> UserResponse:
        """3 - !cmd: run CLI commands

        Allows authenticated admin users to run pre-defined CLI commands
        """
        if self._admins is None:
            logger.warning("Admin nodes not defined. Unable to execute CLI commands.")
            return UserResponse(message="Admin nodes not defined", user_id=user_id)
        elif user_id not in self._admins:
            logger.warning(f"Unauthorized user: {user_id}")
            return UserResponse(message="Unauthorized", user_id=user_id)
        elif self._commands == {}:
            return UserResponse(message="No commands defined", user_id=user_id)
        elif len(msg[1:]) == 0:
            return UserResponse(
                message=f"run {self._prefix}cmd list for a list of commands",
                user_id=user_id,
            )

        # rejoin the command and omit !cmd
        msg_joined = self._rejoin_msg(msg[1:])
        if msg_joined == "list":
            return UserResponse(
                message=",".join(self._commands.keys()), user_id=user_id
            )

        cmd = self._commands.get(msg_joined)
        if cmd is None:
            return UserResponse(message="Command not found", user_id=user_id)
        else:
            logger.info(f"Executing command: {cmd}")
            # TODO: add subprocess run here
            return UserResponse(message="Command executing...", user_id=user_id)

    def _cmd_info(self, user_id: str) -> UserResponse:
        """98 - !i: Pkg info

        Returns service info such as version and URLs
        """
        resp = UserResponse(user_id=user_id, message=f"v{self._version}\n{self._url}")
        return resp

    def _cmd_help(self, user_id: str) -> UserResponse:
        """99 - !h: Help menu

        Returns a list of commands.

        All command functions should start with the command prefix of _cmd_ to be picked up.

        The first line should be formatted as such:

        `{cmd order} - !{cmd prefix}: {description}`
        """
        cmds: list[str] = []
        for name, member in inspect.getmembers(self.__class__, inspect.isfunction):
            # Check if it's a method and has a docstring
            if name.startswith("_cmd_"):
                doc = inspect.getdoc(member)
                if doc:
                    # strip the first line
                    first = doc.split("\n")[0]
                    cmds.append(first)

        # sort the commands by the leading number in the docstring
        # it might be easier to just do this by hand, but this is more fun
        cmds.sort()
        cmd_str = "\n".join(
            [c.split("- ")[-1].replace("!", self._prefix) for c in cmds]
        ).strip()
        return UserResponse(user_id=user_id, message=cmd_str)

    def handle(
        self, text: str, sender_id: str
    ) -> UserResponse | None:
        """Core of the Message Handler

        If returns UserResponse, command accepted.
        If returns None, no action required
        """

        msg = self._prepare_message(text)
        if len(msg) == 0:
            return None

        elif self._is_test(msg):
            return UserResponse(
                user_id=sender_id, message=f"Test received: {self._rejoin_msg(msg)}"
            )

        elif not msg[0].startswith(self._prefix):
            # from here on out, ignore all messages without prefix
            return None

        logger.info(
            "Command received",
            extra={"text": msg, "sender": sender_id},
        )

        match msg[0]:
            case "!cmd":
                return self._cmd_run_command(msg, sender_id)
            case "!w":
                return self._cmd_waypoints(msg, sender_id)
            case "!i":
                return self._cmd_info(sender_id)
            case "!h":
                return self._cmd_help(sender_id)
            case _:
                logger.warning(f'Command not found: {msg[0]}')
                return None
