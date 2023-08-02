import json

from enum import Enum


class ErrorCode(Enum):
    # General error codes
    PARSE_ERROR = -32700
    INCORRECT_REQUEST = -32600
    NO_SUCH_OPERATION = -32601
    INCORRECT_PARAMS = -32602

    # Operation-specific codes
    UNKNOWN_GAME = -40100
    ALREADY_IN_MATCH = -40101
    UNKNOWN_MATCH = -40102
    DUPLICATE_PLAYER = -40103
    INCORRECT_MATCH = -40104

    # game-action codes
    GAME_NOT_PLAYER_TURN = -50100
    GAME_NO_SUCH_ACTION = -50101
    GAME_INCORRECT_ACTION_DATA = -50102
    GAME_INCORRECT_MOVE = -50103

    def __str__(self):
        return ERROR_MESSAGES[self.value]


ERROR_MESSAGES = {
    # General error codes
    ErrorCode.PARSE_ERROR.value: "Parse error",
    ErrorCode.INCORRECT_REQUEST.value: "Incorrect request",
    ErrorCode.NO_SUCH_OPERATION.value: "No such operation",
    ErrorCode.INCORRECT_PARAMS.value: "Incorrect parameters",

    # Operation-specific codes
    ErrorCode.UNKNOWN_GAME.value: "Unknown game",
    ErrorCode.ALREADY_IN_MATCH.value: "Already in a match",
    ErrorCode.UNKNOWN_MATCH.value: "Unknown match",
    ErrorCode.DUPLICATE_PLAYER.value: "Duplicate player name",
    ErrorCode.INCORRECT_MATCH.value: "Incorrect match",

    # game-action codes
    ErrorCode.GAME_NOT_PLAYER_TURN.value: "Action not allowed outside player's turn",
    ErrorCode.GAME_NO_SUCH_ACTION.value: "Unsupported action in game",
    ErrorCode.GAME_INCORRECT_ACTION_DATA.value: "Incorrect data in game action",
    ErrorCode.GAME_INCORRECT_MOVE.value: "Incorrect move"
}



class ChimeraGameException(Exception):

    def __init__(self, details=None):
        self.details = details


class NotPlayerTurn(ChimeraGameException):

    def __init__(self, details=None):
        if details is None:
            details = "It is not your turn."

        super().__init__(details)


class IncorrectActionData(ChimeraGameException):

    def __init__(self, details=None):
        if details is None:
            details = "Incorrect action data"

        super().__init__(details)


class IncorrectMove(ChimeraGameException):

    def __init__(self, details=None):
        if details is None:
            details = "Incorrect move"

        super().__init__(details)


class ChimeraClientException(Exception):
    """
    Base class for all client API exceptions
    """

    def __init__(self, message):
        super().__init__(message)


class ChimeraConnectionRefusedException(ChimeraClientException):
    """
    Raised when the client API is unable to connect to the Chimera server
    """

    def __init__(self, cre):
        self.cre_exc = cre
        super().__init__(str(cre))


class MalformedResponse(ChimeraClientException):
    """
    Raised when the client API receives a malformed response from the
    Chimera server
    """

    def __init__(self, message, response):
        response_json = json.dumps(response, indent=2)
        exc_message = f"Malformed response: {message}\n\n{response_json}"
        super().__init__(exc_message)
        self._response = response


class ErrorResponse(ChimeraClientException):
    """
    Base class for exceptions that stem from an error response
    from the server
    """

    def __init__(self, code, message, data):
        self._code = code
        self._error_message = message
        self._data = data

        exc_message = f"Error {code}: {message}"
        if "details" in data:
            exc_message = f"{exc_message} ({data['details']})"
        super().__init__(exc_message)

    @property
    def code(self):
        return self._code

    @property
    def error_message(self):
        return self._error_message

    @property
    def details(self):
        return self._data.get("details")


class AlreadyInAMatch(ErrorResponse):
    """
    Raised when a player tries to join a match, but they are already in a match.
    """
    pass


class UnknownMatch(ErrorResponse):
    """
    Raised when a player provides an incorrect match identifier
    """
    pass


class DuplicatePlayer(ErrorResponse):
    """
    Raised when a player tries to join a match, but there is already
    a player with the same name in that match.
    """
    pass


class GameNoSuchAction(ErrorResponse):
    """
    Raised when a game action is sent to a match, but the game does
    not support that action.
    """
    pass


class GameIncorrectActionData(ErrorResponse):
    """
    Raised when a game action is sent to a match, but the data
    included in the action is incorrect.
    """
    pass


class GameNotPlayerTurn(ErrorResponse):
    """
    Raised when a player performs an action that can only be
    performed when it is the player's turn.
    """
    pass

class GameIncorrectMove(ErrorResponse):
    pass


ERROR_EXCEPTIONS = {
    ErrorCode.ALREADY_IN_MATCH.value: AlreadyInAMatch,
    ErrorCode.UNKNOWN_MATCH.value: UnknownMatch,
    ErrorCode.DUPLICATE_PLAYER.value: DuplicatePlayer,
    ErrorCode.GAME_NO_SUCH_ACTION.value: GameNoSuchAction,
    ErrorCode.GAME_INCORRECT_ACTION_DATA.value: GameIncorrectActionData,
    ErrorCode.GAME_NOT_PLAYER_TURN.value: GameNotPlayerTurn,
    ErrorCode.GAME_INCORRECT_MOVE.value: GameIncorrectMove
}

