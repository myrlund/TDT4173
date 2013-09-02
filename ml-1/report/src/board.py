import copy, itertools, random

X = "X"
O = "O"
PLAYERS = (X, O)

class Board:
    _dimensions = 3
    
    def __init__(self, initial_board=None):
        if initial_board:
            self._board = copy.deepcopy(initial_board)
        else:
            self._board = [[None for _ in range(self._dimensions)] \
                                 for _ in range(self._dimensions)]
    
    def play(self, coords, player):
        """coords being a tuple of x and y, zero-indexed."""
        x, y = self._validate_coords(coords, allow_occupied=False)
        self._board[y][x] = player
        return self
    
    def get(self, coords):
        x, y = self._validate_coords(coords)
        return self._board[y][x]
    
    def diagonals(self):
        d1 = [self._board[i][i] for i in range(self._dimensions)]
        d2 = [self._board[i][self._dimensions - i - 1] \
                for i in range(self._dimensions)]
        return [d1, d2]
    
    def columns(self):
        return [[self._board[i][j] \
                    for i in range(self._dimensions)] \
                    for j in range(self._dimensions)]
    
    def rows(self):
        return [self._board[i] for i in range(self._dimensions)]
    
    def alignments(self):
        return self.columns() + self.rows() + self.diagonals()
    #######
# class Board: (cont.)
    def alignments_for_player(self, player):
        return [Board.filter_by_player(cells, player)
                    for cells in self.alignments()]
    
    @staticmethod
    def filter_by_player(cells, player):
        return filter(lambda cell: cell == player, cells)
    
    @staticmethod
    def is_winning_combo(cells, player):
        return len(Board.filter_by_player(cells, player)) == Board._dimensions
    
    def is_winner(self, player):
        return any(Board.is_winning_combo(cells, player) \
                    for cells in self.alignments())
    
    def has_winner(self):
        return any(self.is_winner(p) for p in PLAYERS)

    def has_free_spaces(self):
        for i in range(self._dimensions):
            for j in range(self._dimensions):
                if self._board[i][j] is None:
                    return True
        return False
    
    def is_draw(self):
        return not (self.has_free_spaces() or self.has_winner())
    #######
# class Board: (cont.)

    def total_aligned_for_player(self, player):
        player_alignments = self.alignments_for_player(player)
        n_aligned = map(len, player_alignments)
        doubles = filter(lambda l: l > 1 and l < self._dimensions, n_aligned)
        return sum(doubles)
    
    def total_spaces_eligible_for_win(self, player):
        n = 0
        for cells in self.alignments():
            player_cells = Board.filter_by_player(cells, player)
            empty_cells  = Board.filter_by_player(cells, None)
            if len(player_cells) == (self._dimensions - 1) and \
               len(empty_cells) == 1:
                n += 1
        return n
    
    def total_adjacent_opponents(self, player):
        other_player = X if player == O else O
        
        n = 0
        for cells in self.alignments():
            if player in cells:
                opponent_cells = Board.filter_by_player(cells, other_player)
                n += len(opponent_cells)
        return n
    
    #######
    def _validate_coords(self, coords, allow_occupied=True):
        x, y = coords
        if x not in range(self._dimensions) or \
           y not in range(self._dimensions):
            raise ValueError("invalid coords")
        
        if not allow_occupied and self._board[y][x] is not None:
            raise ValueError("(%d, %d) is occupied" % coords)
        
        return coords
    
    def __str__(self):
        return "\n".join([" ".join([(c or " ") for c in row]) \
                            for row in self._board])
#######
# class Board (cont.)
    
    def valid_plays(self):
        return [(j, i) for i in range(self._dimensions) \
                       for j in range(self._dimensions) \
                           if self._board[i][j] is None]
    
    def simulate_play(self, coords, player):
        return Board(self._board).play(coords, player)

def evaluate_board(board, player):
    other_player = X if player == O else O
    
    if board.is_winner(player): return 100.0
    if board.is_winner(other_player): return -100.0
    if board.is_draw(): return 0.0
    
    x = [
        board.total_aligned_for_player(player),
        board.total_aligned_for_player(other_player),
        board.total_spaces_eligible_for_win(player),
        board.total_spaces_eligible_for_win(other_player),
        board.total_adjacent_opponents(player),
    ]
    
    w = [2.0, -2.0, 4.0, -50.0, -0.1]
    
    # Return the $\sum_i{x_iw_i}$
    return sum(map(lambda (x, w): x * w, zip(x, w)))

def fixed_weight_play(board, player):
    valid_plays = board.valid_plays()
    
    results = {}
    best_play = None
    for play in valid_plays:
        simulated_board = board.simulate_play(play, player)
        results[play] = evaluate_board(simulated_board, player)
        
        if best_play is None or results[play] >= results[best_play]:
            best_play = play
    
    return best_play

def random_play(board, player):
    valid_plays = board.valid_plays()
    return valid_plays[random.randint(0, len(valid_plays) - 1)]

strategies = {
    X: fixed_weight_play,
    O: fixed_weight_play,
}

board = Board()
board.play((0, 0), X)
print evaluate_board(board, X)

# Game loop
board = Board()
for player in itertools.cycle(PLAYERS):
    print "%s's turn." % player
    
    strategy = strategies[player]
    play = strategy(board, player)
    board.play(play, player)
    
    print "%s played (%d, %d)." % ((player,) + play)
    print board
    
    if board.has_winner() or board.is_draw():
        print "...aaaand we're done."
        break
