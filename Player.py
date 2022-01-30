import numpy as np
import random

class Board(np.ndarray):
    """
    A new board class that allows us to have nice methods into important
    functionality wrapping the numpy class.
    INPUTS:
    board - a numpy array containing the state of the board using the
            following encoding:
            - the board maintains its same two dimensions
                - row 0 is the top of the board and so is
                  the last row filled
            - spaces that are unoccupied are marked as 0
            - spaces that are occupied by player 1 have a 1 in them
            - spaces that are occupied by player 2 have a 2 in them
    """

    def __new__(cls, a):
        obj = np.asarray(a).view(cls)
        return obj

    def owner_at(self, row, col):
        # Given the encoding above
        if self[row][col] == 0:
            return None
        elif self[row][col] == 1:
            return "player_one"
        elif self[row][col] == 2:
            return "player_two"

    def possible_moves(self):
        possible_moves = []
        # Iterates the boards columns from left to right
        for col in range(self.shape[1]):
            # Iterates the boards rows from bottom to top
            for row in range(self.shape[0]-1, -1, -1):
                # Check that this space has no owner
                if self.owner_at(row, col) is None:
                    possible_moves.append((row, col))
                    # we break here because rows empty above this one
                    # are not valid moves (cant place a disc on nothing)
                    break
        return possible_moves

    def count_series(self, line, player):
        # Counts the size and number of connected components in a board
        count = 0
        connected_magnitudes = []

        for disc in line:
            if disc != player:
                if count <= 1:
                    count = 0
                else:
                    connected_magnitudes.append(count)
                    count = 0
            else:
                count += 1
        if count > 1:
            connected_magnitudes.append(count)
        return connected_magnitudes

    def calculate_score(self, line, player):
        # Determines some score for the size and number of connected
        # components in a line
        connected_components = self.count_series(line, player)
        score = 0
        over = False

        for size in connected_components:
            if size == 2:
                score += 10
            elif size == 3:
                score += 100
            elif size >= 4:
                score += 10000
                over = True
        return score, over

    def get_diagonals(self):
        if self.shape[0] > self.shape[1]:
            largest_side = self.shape[0]
        else:
            largest_side = self.shape[1]
        offset = largest_side * -1

        diagonals = []
        for i in range(offset, largest_side):
            if len(np.diagonal(self, i)) >= 4:
                diagonals.append(np.diagonal(self, i))
                diagonals.append(np.diagonal(np.fliplr(self), i))
        return diagonals

    def connected_heuristic(self, player):
        # A possible heuristic, going to have to implement a basic
        # version in pure numpy
        # Call count_series on all horizontal lines, all vertical lines
        # and both diagonal lines that >= spaces
        total = 0
        for row in self:
            score, over_row = self.calculate_score(row, player)
            total += score

        for col in self.T:
            score, over_col = self.calculate_score(col, player)
            total += score

        for diag in self.get_diagonals():
            score, over_diag = self.calculate_score(diag, player)
            total += score

        if over_row or over_col or over_diag:
            return total, True
        else:
            return total, False

    def play(self, row, col, player):
        # play a disc at the specified row, color
        play_board = np.copy(self)
        state = Board(play_board)
        if state.owner_at(row, col) is None:
            state[row][col] = player
            return state
        else:
            raise Exception("Attempting to play at occupied space")

class AIPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'ai'
        self.player_string = 'Player {}:ai'.format(player_number)


    def opponent(self, player):
        if player == 1:
            opponent = 2
        else:
            opponent = 1
        return opponent


    def evaluation_function(self, board):
        """
        Given the current stat of the board, return the scalar value that
        represents the evaluation function for the current player

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The utility value for the current board
        """
        #state = Board(board)
        player = self.player_number
        opponent = self.opponent(player)

        loss_player, player_won = board.connected_heuristic(player)
        loss_opponent, opponent_won = board.connected_heuristic(opponent)
        # print(f"Player {player} loss: {loss_player}")
        # print(f"Opponent {opponent} loss: {loss_opponent}")

        dynamic = False

        if dynamic:
            if player == 1:
                balanced = False
                offensive = True
                defensive = False
            elif player == 2:
                balanced = False
                offensive = False
                defensive = True
        else:
            balanced = True
            offensive = False
            defensive = False

        if balanced:
            loss = loss_player - loss_opponent
        elif offensive:
            loss = loss_player - (loss_opponent / 3)# encourage offensive play
        elif defensive:
            loss = loss_player - (loss_opponent * 3)# encourage defensive play

        if opponent_won:
            return -1000000, opponent #f"Winner is opponent: {opponent}"
        if player_won:
            return  1000000, player #f"Winner is player: {player}"

        return loss, None

    def min_value(self, state, alpha, beta, depth):
        utility, winner = self.evaluation_function(state)
        if winner:
            print(f"Min call - player {winner} will win at state:")
            print(state)
            return utility
        if depth == 0:
            #print("Depth is 0")
            return utility

        value = 100000
        for row, col in state.possible_moves():
            new_state = state.play(row, col, self.opponent(self.player_number))
            value = min(value, self.max_value(new_state, alpha, beta, depth-1))
            # pruning
            if value <= alpha:
                return value
            beta = max(beta, value)

        return value

    def max_value(self, state, alpha, beta, depth):
        utility, winner = self.evaluation_function(state)
        if winner:
            print(f"Max call - player {winner} will win at state:")
            print(state)
            return utility
        if depth == 0:
            #print("Depth is 0")
            return utility

        value = -100000
        for row, col in state.possible_moves():
            new_state = state.play(row, col, self.player_number)
            value = max(value, self.min_value(new_state, alpha, beta, depth-1))
            # prunning
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value

    def max_exp_val(self, state, depth):
        utility, winner = self.evaluation_function(state)
        if winner:
            print(f"Player {winner} has won")
            return utility
        if depth == 0:
            #print("Depth is 0")
            return utility
        v = -100000

        for row, col in state.possible_moves():
            new_state = state.play(row, col, self.player_number)
            v = max(v, self.exp_value(new_state, depth-1))
        return v

    def exp_value(self, state, depth):
        utility, winner = self.evaluation_function(state)
        if winner:
            print(f"Player {winner} has won")
            return utility
        if depth == 0:
            print("Depth is 0")
            return utility

        v = 0
        count = 0
        for row, col in state.possible_moves():
            new_state = state.play(row, col, self.opponent(self.player_number))
            v += self.max_exp_val(new_state, depth-1)
            count += 1

        return v / count


    def get_alpha_beta_move(self, board):
        """
        Given the current state of the board, return the next move based on
        the alpha-beta pruning algorithm

        This will play against either itself or a human player

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The 0 based index of the column that represents the next move
        """
        state = Board(board)

        alpha = float('-inf')
        beta  = float('inf')
        depth = 6
        best_val = 0
        # random col thats avail
        best_col = random.choice(state.possible_moves())[1]
        best_row = 0

        for row, col in state.possible_moves():
            new_state = state.play(row, col, self.player_number)
            v = self.min_value(new_state, alpha, beta, depth)
            if v > best_val:
                # print(f"Player {self.player_number} found good play at {col}")
                best_val = v
                best_col = col
                best_row = row

        print(f"Player {self.player_number} picked play at {best_col}")
        return best_col
        raise NotImplementedError('Whoops I don\'t know what to do')

    def get_expectimax_move(self, board):
        """
        Given the current state of the board, return the next move based on
        the expectimax algorithm.

        This will play against the random player, who chooses any valid move
        with equal probability

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The 0 based index of the column that represents the next move
        """
        state = Board(board)

        depth = 5
        best_val = 0
        # middle column
        best_col = state.shape[1]//2
        best_row = 0

        for row, col in state.possible_moves():
            new_state = state.play(row, col, self.player_number)
            v = self.exp_value(new_state, depth)
            if v > best_val:
                best_val = v
                best_col = col
                best_row = row

        return best_col
        raise NotImplementedError('Whoops I don\'t know what to do')

class RandomPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'random'
        self.player_string = 'Player {}:random'.format(player_number)

    def get_move(self, board):
        """
        Given the current board state select a random column from the available
        valid moves.

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The 0 based index of the column that represents the next move
        """
        valid_cols = []
        for col in range(board.shape[1]):
            if 0 in board[:,col]:
                valid_cols.append(col)

        return np.random.choice(valid_cols)


class HumanPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'human'
        self.player_string = 'Player {}:human'.format(player_number)

    def get_move(self, board):
        """
        Given the current board state returns the human input for next move

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The 0 based index of the column that represents the next move
        """

        valid_cols = []
        for i, col in enumerate(board.T):
            if 0 in col:
                valid_cols.append(i)

        move = int(input('Enter your move: '))

        while move not in valid_cols:
            print('Column full, choose from:{}'.format(valid_cols))
            move = int(input('Enter your move: '))

        return move
