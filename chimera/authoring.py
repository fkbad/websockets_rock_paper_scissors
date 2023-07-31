from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class Player:
    """
    Simple class for storing information about a player in a game.

    Should not be instantiated directly, but there are several
    Game methods that will return instances of this class.
    """

    game: Game
    name: str
    id: Optional[int]

    def __init__(self, game: Game, player_name: str):
        self.game = game
        self.name = player_name
        self.id = None


class Game(ABC):
    """
    Base class for Chimera games. Adding a game to Chimera involves
    subclassing this class, and implementing all its abstract methods.
    Also provides a number of convenience methods that can help with
    implementing a game.

    Each time a new match of a game is created, an instance of a Game
    class will be created and associated with that specific match.
    The purpose of the Game class is to specify the logic of the game.

    A Game will have one more players, represented by Player objects.
    These Player objects are created and added to the game by the backend
    (based on the players that join a match). Each player has an
    integer identifier, numbered from 0 (e.g., in a four-player game,
    the players' identifiers would be 0, 1, 2, 3). Currently,
    these identifiers are set in the order in which players join a match.
    """

    _game_options: dict
    _players: List[Player]
    _players_by_name: Dict[str, Player]
    _current_player_id: int
    _state_updated: bool

    def __init__(self, game_options: dict):
        """ Constructor

        Should be called from the subclass constructor.

        Args:
            game_options: Dictionary with game-specific options.
        """
        self._game_options = game_options
        self._players = []
        self._players_by_name = {}
        self._state_updated = False

    @property
    @abstractmethod
    def min_players(self) -> int:
        """Returns the minimum number of players in the game

        A game cannot start until at least these many players
        have joined a match.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max_players(self) -> int:
        """Returns the maximum number of players in the game

        The backend will not allow more than these many players
        to join a match.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def game_state(self) -> dict:
        """Returns the game's state"""
        raise NotImplementedError

    @property
    @abstractmethod
    def done(self) -> bool:
        """Returns True if the game is over, False otherwise."""
        raise NotImplementedError

    @property
    @abstractmethod
    def winner(self) -> Player:
        """Returns the winning player, or None of there is no winner"""
        raise NotImplementedError

    @abstractmethod
    def on_start(self) -> None:
        """
        This method can be used to specify code that must run
        right before the game starts. Unlike the constructor,
        when this method is called by Chimera, all the players
        have already been added to the game.

        Returns: None
        """
        raise NotImplementedError

    @abstractmethod
    def on_end(self) -> None:
        """
        This method can be used to write code that must run
        right once the game over (e.g., to perform any
        clean-up tasks, freeing up resources, etc.)

        Returns: None
        """
        pass

    # CONVENIENCE METHODS
    #
    # These methods can be used from the implementation of the
    # game actions

    @property
    def num_players(self) -> int:
        """Returns the number of players in the game"""
        return len(self._players)

    def get_player_by_id(self, player_id: int) -> Player:
        """ Gets the Player object whose identifier is player_id

        Args:
            player_id: Player identifier

        Raises:
            ValueError: if the identifier is incorrect

        Returns: Player object with the given identifier

        """
        if player_id < 0:
            raise ValueError(f"Invalid player_id: {player_id}")
        try:
            return self._players[player_id]
        except IndexError:
            raise ValueError(f"Invalid player_id: {player_id}")

    def notify_update(self) -> None:
        """
        If called, notifies the backend that the game's state
        has changed, and that a notification should be sent to
        the players.

        Returns: None

        """
        self._state_updated = True

    # PRIVATE METHODS
    #
    # These methods should only be called from the backend code

    def _create_player(self, name: str) -> Player:
        """ Creates a new player for this game

        Args:
            name: Player's name

        Returns: Player object

        """
        return Player(self, name)

    def _add_player(self, player: Player) -> None:
        """ Adds a player to the game

        Args:
            player: Player to add

        Returns: None
        """
        self._players.append(player)
        player.id = len(self._players) - 1
        self._players_by_name[player.name] = player

    def _reset_state_updated(self) -> None:
        """Resets the updated state flag"""
        self._state_updated = False


class TwoPlayerGame(Game, ABC):
    """Convenience class for two-player games

    Only implements the min_players and max_players methods,
    to require exactly two players. Leaves all other
    abstract methods from Game unimplemented.
    """

    def __init__(self, game_options):
        super().__init__(game_options)

    @property
    def min_players(self):
        return 2

    @property
    def max_players(self):
        return 2


class TurnBasedGame(Game, ABC):
    """
    Class for implementing turn-based games.

    In this type of game, the players take turns
    making moves (at the moment, we only support starting
    with the first player, and round-robin-ing between
    all the players). Once all players have taken a turn,
    they have completed a *round*.

    This class includes convenience methods related to
    querying and enforcing these turns.
    """

    _current_player_id: int

    def __init__(self, game_options: dict):
        """ Constructor

        Should be called from the subclass constructor.

        Args:
            game_options: Dictionary with game-specific options.
        """
        super().__init__(game_options)
        self._current_player_id = 0

    @property
    def current_player(self) -> Player:
        """Returns the current player (i.e., the player whose turn it currently is)"""
        return self._players[self._current_player_id]

    def turn_to_next_player(self) -> None:
        """ Advances the turn to the next player

        Returns: None
        """
        next_id = (self._current_player_id + 1) % self.num_players
        self._current_player_id = next_id

    @property
    def is_end_of_round(self) -> bool:
        """
        Returns True if the current player is the last player in
        the current round, False otherwise
        """
        return self._current_player_id == self.num_players - 1


class TwoPlayerTurnBasedGame(TurnBasedGame, ABC):

    """Convenience class for turn-based two-player games

    Only implements the min_players and max_players methods,
    to require exactly two players. Leaves all other
    abstract methods from TurnBasedGame unimplemented.
    """

    def __init__(self, game_options):
        super().__init__(game_options)

    @property
    def min_players(self):
        return 2

    @property
    def max_players(self):
        return 2
