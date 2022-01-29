import numpy as np

class AIPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'ai'
        self.player_string = 'Player {}:ai'.format(player_number)

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
            for size in connected_components:
                if size == 2:
                    score += 1
                elif size == 3:
                    score += 10
                elif size >= 4:
                    score += 100
            return score

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
            score = 0
            for row in self:
                score += self.calculate_score(row, player)

            for col in self.T:
                score += self.calculate_score(col, player)

            for diag in self.get_diagonals():
                score += self.calculate_score(diag, player)

            return score


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
        state = Board(board)
        player = self.player_number

        if player == 1:
            opponent = 2
        else:
            opponent = 1

        loss = state.connected_heuristic(player)
        loss -= state.connected_heuristic(opponent)

        return loss

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
