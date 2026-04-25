import numpy as np
import a2_260408 as cg_logic

DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

class CoGanhEnv:
    def __init__(self):
        self.board = cg_logic.init_board()
        self.turn = 1 # 1 là phe X, -1 là phe O
        self.move_count = 0
        self.max_moves = 100
        self.mo_moves = [] # Danh sách nước đi bắt buộc do luật "Mở"

    def reset(self):
        self.board = cg_logic.init_board()
        self.turn = 1
        self.move_count = 0
        self.mo_moves = []
        return self.get_state()

    def get_state(self):
        state = np.zeros((3, 5, 5), dtype=np.float32)
        for r in range(5):
            for c in range(5):
                if self.board[r][c] == self.turn:
                    state[0, r, c] = 1.0
                elif self.board[r][c] == -self.turn:
                    state[1, r, c] = 1.0
        state[2, :, :] = 1.0 # Current turn indicator
        return state

    def encode_action(self, start, end):
        start_r, start_c = start
        end_r, end_c = end
        dir_r, dir_c = end_r - start_r, end_c - start_c
        try: dir_idx = DIRECTIONS.index((dir_r, dir_c))
        except ValueError: return -1
        return (start_r * 5 + start_c) * 8 + dir_idx

    def decode_action(self, action_idx):
        square_idx, dir_idx = action_idx // 8, action_idx % 8
        start_r, start_c = square_idx // 5, square_idx % 5
        dir_r, dir_c = DIRECTIONS[dir_idx]
        return ((start_r, start_c), (start_r + dir_r, start_c + dir_c))

    def get_valid_actions(self):
        if len(self.mo_moves) > 0: moves = self.mo_moves
        else: moves = cg_logic.get_valid_moves(self.board, self.turn)
        
        valid_actions = [self.encode_action(m[0], m[1]) for m in moves]
        return [a for a in valid_actions if a != -1]

    def step(self, action_idx):
        valid_actions = self.get_valid_actions()
        if action_idx not in valid_actions:
            return self.get_state(), -10.0, True, {"legal": False}

        move = self.decode_action(action_idx)
        my_pieces_before = sum([row.count(self.turn) for row in self.board])
        enemy_pieces_before = sum([row.count(-self.turn) for row in self.board])

        self.mo_moves = cg_logic.act_moves(move, self.turn, self.board)
        self.move_count += 1

        my_pieces_after = sum([row.count(self.turn) for row in self.board])
        enemy_pieces_after = sum([row.count(-self.turn) for row in self.board])

        reward = ((my_pieces_after - my_pieces_before) + (enemy_pieces_before - enemy_pieces_after)) * 10.0
        done = (enemy_pieces_after == 0) or (my_pieces_after == 0) or (self.move_count >= self.max_moves)
        
        # Thưởng/phạt lớn khi ván cờ kết thúc
        if done:
            if enemy_pieces_after == 0: # Thắng
                reward += 1000.0
            elif my_pieces_after == 0: # Thua
                reward -= 1000.0
        
        self.turn *= -1 
        return self.get_state(), reward, done, {"legal": True}