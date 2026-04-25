import random
import a2_260408 as cg_logic

def move(board, player, remain_time=0, mo_moves=None):
    moves = cg_logic.get_valid_moves(board, player)
    if len(moves) == 0:
        return None
        
    if mo_moves and len(mo_moves) > 0:
        for m in moves:
            if m in mo_moves:
                return m
                
    index_move = random.randint(0, len(moves) - 1)
    chose_move = moves[index_move]
    
    for item in moves:
        start = item[0]
        end = item[1]
        enemy = player * (-1)
        
        # Cần cập nhật bàn cờ copy trước khi kiểm tra gánh và chẹt
        board_copy = cg_logic.copy_board(board)
        board_copy[start[0]][start[1]] = 0   
        board_copy[end[0]][end[1]] = player
        
        # Kiểm tra gánh
        l_ganh = cg_logic.ganh(board_copy, end[0], end[1], enemy)
        if len(l_ganh) > 0:
            chose_move = item
            return chose_move

        # Kiểm tra chẹt
        if cg_logic.chet(board_copy, enemy):
            return item
            
    return chose_move
