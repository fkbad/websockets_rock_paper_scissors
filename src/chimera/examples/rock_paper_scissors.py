# for some reason, importing as chimera.authoring didn't work
from typing import Dict, List, Optional, Union
from ..authoring import TwoPlayerGame, Player
from .. import exceptions as exc


class RockPaperScissors(TwoPlayerGame):
    # for now, not enough involved in status to make it separate
    # STATUS_GAME_NOT_STARTED = "not-started"
    # STATUS_WAITING_FOR_MOVES = "waiting-for-moves"
    # STATUS_PROCESSING_CURRENT_ROUND = "processing-current-round"
    # STATUS_DONE = "done"

    def __init__(self, game_options=dict()):
        # game_options is, if not specified, the empty dictionary
        super().__init__(game_options) 

        # simply a list where [0] is the first players points
        # can be indexed by player.id because 
        # id's are assigned in ascending order from 0 as players join
        self.points: Optional[List[int]] = None

        # move history per round, stored as a list of lists
        # add a move by doing:
        # self.history.append([p1_move, p2_move, id of player who won the round (or None) ])
        self.history: Optional[List[List[Optional[int]]]]= None

        # simply a list where [0] is the first players move this round
        # can be indexed by player.id because 
        # id's are assigned in ascending order from 0 as players join
        self.current_round_moves: Optional[List[Optional[int]]] = None

        # ID of the winning player for the current round, if completed.
        # None in the case of a Tie, and if the round is in progress
        self.current_round_winner_id: Optional[int] = None

        # TODO, have this grab from game_options
        self.points_to_win:int = 3


    @property
    def game_state(self):
        """
        returns the game state of the Game
        should only be called after game has started (.on_start() called) by the server

        Outputs:
            state dictionary: {
                "current_round" : {
                        "moves" : {
                            "[player_1_name]" : player 1's move,
                            "[player_2_name]" : player 2's move,
                            },
                        "winner" : Optional[Player name] (optional in case of a tie)
                        },
                "points" {
                    "[player_1_name]" : player 1's score,
                    "[player_2_name]" : player 2's score,
                    },
                "history" : [
                        append-only list of all "completed" rounds. 
                        where a completed round is one where both
                        players have given a move.
                        Format for each entry is the same as the 
                        "current_round" parameter
                        ]
                }
        """
        state = {}

        # assert for type checking that the game has started 
        # and the initial None values are gone
        assert self.history is not None
        assert self.points is not None
        assert self.current_round_moves is not None

        players = [self.get_player_by_id(0),self.get_player_by_id(1)] 
        player_names = [player.name for player in players]

        # first round
        current_round = self.get_current_round_for_game_state(player_names = player_names)
        state["current_round"] = current_round

        # now points
        points = self.get_points_for_game_state(player_names = player_names)
        state["points"] = points

        # now history
        history_list = self.get_history_list_for_game_state(player_names=player_names)
        state["history"] = history_list

        return state

    @property
    def done(self) -> bool:
        """
        returns whether or not the entire game is done

        for RPS, this means that one player has reached the point threshold to win
        """
        threshold = self.points_to_win

        # assert for type checking, 
        # done should not be called before `on_start()` which instantiates self.points
        assert self.points is not None
        # this check should be sufficient as `self.done` should be checked after every move
        # and since points start at 0 and can only be incremented by 1
        # checking at every change should means this is enough

        return threshold in self.points

    @property
    def winner(self):
        if self.done:
            # there must be points at this point
            assert self.points

            if self.points[0] > self.points[1]:
                return self.get_player_by_id(0)
            elif self.points[0] < self.points[1]:
                return self.get_player_by_id(1)
            else:
                return None
        else:
            return None

        
    def on_start(self):
        self.points = [0] * self.max_players
        self.history = []
        self.current_round_moves = [None,None]

        # don't actually notify update since that 
        # is currently designed to only happen when 
        # one round is resolved 
        # self.notify_update()

    def on_end(self):
        pass


    def get_current_round_for_game_state(self,player_names: List[str]) -> Dict[str,Union[Dict[str,str], str]]:
        """
        return the properly formatted current_round dictionary
        to be used in game_state

        "current_round" : {
                "moves" : {
                    "[player_1_name]" : player 1's move,
                    "[player_2_name]" : player 2's move,
                    },
                "winner" : Optional[Player name] (optional in case of a tie)
                },
        """

        assert self.history is not None
        assert self.points is not None
        assert self.current_round_moves is not None

        current_round = {}

        # construct move dict first

        # if the round is in progress, this will then report None
        # as the moves haven't happened yet
        move_dict = {player_name:player_move for player_name,player_move in zip(player_names,self.current_round_moves)}

        current_round["moves"] = move_dict

        # next get the winner

        # by default, current winner is None
        current_round_winner = None
        if self.current_round_winner_id is not None:
            # grab the name of the current round's winner
            current_round_winner = player_names[self.current_round_winner_id]

        # regardless of if the winner is None, add it to the current_round dict
        current_round["winner"] = current_round_winner

        return current_round

    def get_points_for_game_state(self,player_names: List[str]) -> Dict[str,int]:
        """
        return points dictionary for the purposes of reporting game state

        "points" {
            "[player_1_name]" : player 1's score,
            "[player_2_name]" : player 2's score,
            },
        """
        assert self.points is not None

        points = {player_name: player_score for player_name,player_score in zip(player_names,self.points)}

        return points



    def get_history_list_for_game_state(self,player_names: List[str]) -> List[Dict[str,Union[Dict[str,str], str]]]:
        """
        return the properly formatted list of rounds for the purposes of reporting
        game state.

        history[0] is the 1st played round
        history[-1] is the most recently completed round, where a round has the below format

        "round" : {
                "moves" : {
                    "[player_1_name]" : player 1's move,
                    "[player_2_name]" : player 2's move,
                    },
                "winner" : Optional[Player name] (optional in case of a tie)
                },
        """
        # self.history is of the format: 
        # [p1_move, p2_move, id of player who won the round (or None)]

        history = []

        # assert len(history[0]) == 3
        assert self.history is not None

        p1_name, p2_name = player_names
        for p1_move,p2_move,optional_winner_id in self.history:
            round = {}
            moves = {p1_name:p1_move, 
                     p2_name:p2_move}

            winner_name = None
            if optional_winner_id is not None:
                winner_name = player_names[optional_winner_id]

            round["moves"] = moves
            round["winner"] = winner_name

            history.append(round)

        return history



    def action_move(self,player: Player,data: str):
        """
        method called when a player sends a "move" game-action request 
        to the server

        specifically, they sent a request message for this match 
        with the message["params"] containing the "action":"move"

        Inputs:
            player: Player object corresponding to the player making a move

            data: the "data" field of the params. 
                    I specify this to be either "Rock", "Paper", or "Scissors"

                    considering adding another field for an incompleted move or disconnect

        Outputs:
            result parameter of the response message to be sent out to 
            all players, only to be done on a successfully done game-action

            otherwise, raises an exception
        """
        if self.done:
            raise exc.GameNotPlayerTurn

        player_choice = data

        player_id = player.id


        # check if player can make a move right now
        # history is only set to an empty list once the game has started (.on_start() called)
        # if the player hasn't made a move, update the current moves

        # if the player has already made a move this round, let them update it 
        # so long as the other player hasn't already made a move

        # check if the round is over, if so, update points

        # check if the game is over, notifying thusly


