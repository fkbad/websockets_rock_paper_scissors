# import this so I can reference the class Move
# inside of itself. This postpones type evaluation
from __future__ import annotations

from typing import Dict, List, Optional, Set, Union

# for some reason, importing as chimera.authoring didn't work
from ..authoring import TwoPlayerGame, Player
from .. import exceptions as exc

# for personal reference :)
RPSLS_RULES="""
            Rock crushes scissors.
            Rock crushes lizard

            Scissors cuts paper
            Scissors decapitates lizard

            Paper covers rock
            Paper disproves Spock

            Lizard poisons Spock
            Lizard eats paper

            Spock vaporizes rock
            Spock smashes scissors
            """

def get_move_dict_for_game(subgame_id:str) -> Dict[str,Move]:
    """
    function to return the Move set 
    for any rock paper scissors like game

    used to abstract away the definition of what valid move sets
    and relationship are for a given game

    Input:
        subgame_id:the id for the variety of RPS, 
                should eventually be provided via the game_options in 
                RockPaperScissors() creation

            the currently accepted subgame_id's are:
                "rps" : classic rock paper scissors
                "rpsls" : rock paper scissors lizard spock
                          https://rpsls.net

    Output:
        Dictionary of all allowable moves for the game
        with each Move having their `Move.moves_i_beat` set filled in

        stored as : {
                "move_name" : Move
                }
    """

    returned_move_set: Set[Move] = set()
    match subgame_id:
        case "rps":
            # create moves
            rock = Move("rock")
            paper = Move("paper")
            scissors = Move("scissors")

            # add relationships
            rock.add_beats(scissors)
            paper.add_beats(rock)
            scissors.add_beats(paper)

            returned_move_set = {rock,paper,scissors}

        case "rpsls":
            # create moves
            rock = Move("rock")
            paper = Move("paper")
            scissors = Move("scissors")
            lizard = Move("lizard")
            spock = Move("spock")

            # add relationships
            # TODO add support for flavor text (Lizard "poisons" Spock)

            # rock
            rock.add_beats(scissors)
            rock.add_beats(lizard)

            # scissors
            scissors.add_beats(paper)
            scissors.add_beats(lizard)

            # paper
            paper.add_beats(rock)
            paper.add_beats(spock)

            # lizard
            lizard.add_beats(spock)
            lizard.add_beats(paper)

            # spock
            spock.add_beats(rock)
            spock.add_beats(scissors)

            returned_move_set = {rock,paper,scissors,lizard,spock}

        case _:
            # TODO, change this to instead be an InvalidGameOptions error 
            # if we decide to make that exist
            raise exc.IncorrectActionData(details=f"provided RPS-subgame id: {subgame_id} which is not either RPS or RPSLS")

    # return whatever move set has been constructed
    # transform set into dictionary to return
    return_dict = {move.name:move for move in returned_move_set}
    return return_dict

class Move:
    """
    class for Moves in both rock paper scissors and 
    rock paper scissors lizard spock

    generalized to be used regardless of game
    """
    name: str
    moves_i_beat: Set[Move]
    def __init__(self,name:str) -> None:
        """
        Inputs:
            name: the name of the move, 
                eg: "rock", "lizard", "john"
        """
        self.name = name
        self.moves_i_beat = set()

    def __str__(self) -> str:
        header = ""
        name = self.name.upper().rjust(10) 
        joiner = " beats: "
        beats = "[" + ", ".join([str(move.name).ljust(8) for move in self.moves_i_beat]) + "]"

        return_string = header + name + joiner + beats
        return return_string

    def add_beats(self,Move) -> None:
        """
        takes in a move and adds it to the self.moves_i_beat set

        Inputs:
            a valid Move object

        Outputs:
            nothing
        """
        self.moves_i_beat.add(Move)

    def beats(self,opponent_move:Move) -> bool:
        """
        returns whether or not this move beats the opponents

        Input:
            some Move

        Output:
            True if the this move beats the opponents
            False otherwise (or the the provided `opponent_move` is anything besides a Move)
        """
        return opponent_move in self.moves_i_beat


class RockPaperScissors(TwoPlayerGame):
    """
    class to represent any RockPaperScissors variant.

    variance is handled through the "subgame_id" field that is fed into
    get_move_set_for_game(subgame_id=)

    """
    VALID_SUBGAME_IDS = {
            "rps" : "standard rock paper scissors",
            "rpsls" :  "rock paper scissors lizard spock"
            }

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
        self.current_round_moves: Optional[List[Optional[Move]]] = None

        # ID of the winning player for the current round, if completed.
        # None in the case of a Tie, and if the round is in progress
        self.current_round_winner_id: Optional[int] = None

        # TODO, have this grab from game_options
        self.points_to_win:int = 3

        # Unique Identified for the variant of RPS
        # valid options and their descriptions found in
        # RockPaperScissors.VALID_SUBGAME_IDS

        # TODO have this grab from game options

        # self.subgame_id: str = "rpsls"
        self.subgame_id: str = "rps"

        self.valid_moves: Dict[str,Move] = get_move_dict_for_game(self.subgame_id)


    @property
    def game_state(self):
        """
        returns the game state of the Game
        should only be called after game has started (.on_start() called) by the server

        Outputs:
            state dictionary: {
                "game_type" : {
                    "id" : "rps" , ID corresponding to the particular subgame
                    "description" : "standard rock paper scissors" description of the subgame
                    }
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

        # first game type
        game_type_dict = self.get_game_type_for_game_state()
        state["game_type"] = game_type_dict

        # now round
        current_round = self.get_current_round_for_game_state(player_names= player_names)
        state["current_round"] = current_round

        # now points
        points = self.get_points_for_game_state(player_names= player_names)
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
            "result" parameter of the response message to be sent out to 
            all players, only to be done on a successfully done game-action

            otherwise, raises an exception

            result format for a move is:
                "result" : {
                        "move": move that the server processed
                        }

            this is so the client gets feedback on what the server thinks they sent

        Raises:
            NotPlayerTurn
            IncorrectActionData
            IncorrectMove

        """
        result = {}

        # get the Move object (exception is raised if invalid name is provided)
        player_move = self.get_move_from_player_data(data)

        move_completed: str = self.play_move(player=player,player_move=player_move)

        result["move"] = move_completed

        return result

        # check if player can make a move right now
        # history is only set to an empty list once the game has started (.on_start() called)
        # if the player hasn't made a move, update the current moves

        # if the player has already made a move this round, let them update it 
        # so long as the other player hasn't already made a move

        # check if the round is over, if so, update points

        # check if the game is over, notifying thusly

    def play_move(self,player:Player, player_move: Move) -> str:
        """
        method to actually play a move from a particular player
        
        Input:
            player: Player object corresponding to whoever is trying to make the move
            player_move: validated Move object the player is trying to do

        Output:
            the name of the move that was successfully completed, if so

        Side Affects:
            updates the current_round moves
            updates the overall points if a round is finished
            updates the history if the round completes
        """
        """
        workflow:
            check if this player can make a move this round:
                raise NotPlayerTurn if they can't

            if they can make a move:
                update the current round moves

            if the round is not done yet, return and call it a day

            if the round is done (both players have played a move), 
            process it and notify update
        """
        player_id = player.id
        assert self.current_round_moves is not None
        assert player_id is not None
        
        # check if player can move

        recorded_player_move = self.current_round_moves[player_id]
        if recorded_player_move is not None:
            raise exc.NotPlayerTurn(
                    details=f"you already have made a move this round : {recorded_player_move}")

        else:
            # no recorded move for player this round
            self.current_round_moves[player_id] = player_move
            recorded_move = self.current_round_moves[player_id]
            assert isinstance(recorded_move,Move)
            
            if not self.current_round_over:
                # if the rounds not over after making the move
                # then we're still waiting on the other player
                return recorded_move.name

            else:
                # round is over!
                self.process_current_round()    
                self.notify_update()
                return recorded_move.name
            

            


    @property
    def current_round_over(self) -> bool:
        """
        returns whether or not the current round is over and ready to be processed

        Inputs:
            nothing, will be looking at self.current_round_moves

        Outputs:
            True if both players have made a move (current_round_moves has two moves in it)
            False if at least one player hasn't made a move yet
        """
        # should never be called before on_start()
        assert self.current_round_moves is not None

        # is_empty_move = None in self.current_round_moves

        # # if there are no empty moves, then the round is done!
        # return not is_empty_move

        all_moves = all(isinstance(move,Move) for move in self.current_round_moves)
        return all_moves

    def get_move_from_player_data(self,player_move_string:str):
        """
        returns the Move object from the games set of moves
        for a string provided from a players `move` game-action

        Inputs:
            player_move_string: the string provided from the "data" field
            of the "params" field of their request

        Outputs:
            the Move object with the same name as the player_move_string

        Raises:
            IncorrectMove : when the provided move name is not in 
                            this game's valid moves
        """
        move = self.valid_moves.get(player_move_string)

        if move is None:
            raise exc.IncorrectMove
        else:
            return move

    def get_game_type_for_game_state(self) -> Dict[str,Dict[str,str]]:
        """
        return the game_type dict as required for game_state

        "game_type" : {
            "id" : "rps" , ID corresponding to the particular subgame
            "description" : "standard rock paper scissors" description of the subgame
            }
        """
        game_type = {}
        game_type["id"] = self.subgame_id
        game_type["description"] = RockPaperScissors.VALID_SUBGAME_IDS[self.subgame_id]

        return game_type

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
        move_dict: Dict[str,str] = {}

        for player_name,player_move in zip(player_names,self.current_round_moves):
            if player_move is not None:
                move_dict[player_name] = player_move.name
            else:
                move_dict[player_name] = str(None)

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





