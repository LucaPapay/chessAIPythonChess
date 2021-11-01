import operator

import chess
import chess.svg
import chess.polyglot
import pygame
import random
import chess.engine

from time import sleep
import time

board = chess.Board()

tilesize = 120

white = (238, 238, 213)
black = (125, 148, 93)
true_black = (0, 0, 0)

score = 0
pos_evaluated = 0
quiesce_search = 0
best_engine_score = 0
used_trans_table_lookup = 0

min_max_time = 0
quisce_time = 0
sort_time = 0
draw_time = 0
eval_time = 0

time_limit = 100
should_use_hash_table = True
should_null_move = True

board_value = 0

pygame.init()
pygame.font.init()

surface = pygame.display.set_mode((12 * tilesize, 8 * tilesize))
font = pygame.font.Font(pygame.font.get_default_font(), 20)
pygame.display.set_caption("Luca's Chess Ai")

pawn_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

knights_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

bishops_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]

rooks_table = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0]

queens_table = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]

kings_table = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]

images = {'wK': pygame.transform.scale(pygame.image.load("images/wK.png"), (tilesize, tilesize)),
          'wQ': pygame.transform.scale(pygame.image.load("images/wQ.png"), (tilesize, tilesize)),
          'wp': pygame.transform.scale(pygame.image.load("images/wp.png"), (tilesize, tilesize)),
          'wR': pygame.transform.scale(pygame.image.load("images/wR.png"), (tilesize, tilesize)),
          'wN': pygame.transform.scale(pygame.image.load("images/wN.png"), (tilesize, tilesize)),
          'wB': pygame.transform.scale(pygame.image.load("images/wB.png"), (tilesize, tilesize)),
          'bK': pygame.transform.scale(pygame.image.load("images/bK.png"), (tilesize, tilesize)),
          'bQ': pygame.transform.scale(pygame.image.load("images/bQ.png"), (tilesize, tilesize)),
          'bp': pygame.transform.scale(pygame.image.load("images/bp.png"), (tilesize, tilesize)),
          'bR': pygame.transform.scale(pygame.image.load("images/bR.png"), (tilesize, tilesize)),
          'bN': pygame.transform.scale(pygame.image.load("images/bN.png"), (tilesize, tilesize)),
          'bB': pygame.transform.scale(pygame.image.load("images/bB.png"), (tilesize, tilesize))}

pv = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 450,
    chess.QUEEN: 950,
    chess.KING: 20000
}

piece_values = [100, 320, 330, 450, 950]

tables = [pawn_table, knights_table, bishops_table, rooks_table, queens_table, kings_table]

move_history = []

trans_table = dict()
remember_move = None
best_move = None


class hash_entry:
    def __init__(self, zobrist, depth, score, move, flag):
        self.zobrist = zobrist
        self.depth = depth
        self.score = score
        self.move = move
        self.flag = flag


def draw_board(surface):
    s = time.time()
    draw_board_background(surface)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        draw_piece(surface, square, piece)
    global draw_time
    draw_time = time.time() - s


def draw_piece(surface, square, piece, sidebar=False):
    col = square % 8
    row = square // 8
    #  print(str(row) + str(col) + str(piece.color))
    if sidebar:
        col += 8

    row = 8 - row - 1

    p_string = ""
    if piece.color:
        p_string = p_string + "w"
    else:
        p_string = p_string + "b"

    if piece.piece_type == 1:
        p_string = p_string + "p"

    if piece.piece_type == 2:
        p_string = p_string + "N"
    if piece.piece_type == 3:
        p_string = p_string + "B"
    if piece.piece_type == 4:
        p_string = p_string + "R"
    if piece.piece_type == 5:
        p_string = p_string + "Q"
    if piece.piece_type == 6:
        p_string = p_string + "K"

    surface.blit(images[p_string], pygame.Rect(col * tilesize, row * tilesize, tilesize, tilesize))


def draw_board_background(surface):
    font = pygame.font.Font(pygame.font.get_default_font(), 36)
    for i in range(0, 8):
        for j in range(0, 8):
            lightsquare = (i + j) % 2 == 0
            color = white if lightsquare else black
            pygame.draw.rect(surface, color, (j * tilesize, i * tilesize, tilesize, tilesize))


def eval_board_start():
    global eval_time
    s = time.time()
    pieces = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        if piece.color == chess.WHITE:
            pieces += pv[piece.piece_type]
        else:
            pieces -= pv[piece.piece_type]

    wptv = sum(pawn_table[i] for i in board.pieces(chess.PAWN, chess.WHITE))
    bptv = sum(pawn_table[chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK))
    wRtv = sum(rooks_table[i] for i in board.pieces(chess.ROOK, chess.WHITE))
    bRtv = sum(rooks_table[chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK))
    wNtv = sum(knights_table[i] for i in board.pieces(chess.KNIGHT, chess.WHITE))
    bNtv = sum(knights_table[chess.square_mirror(i)] for i in board.pieces(chess.KNIGHT, chess.BLACK))
    wBtv = sum(bishops_table[i] for i in board.pieces(chess.BISHOP, chess.WHITE))
    bBtv = sum(bishops_table[chess.square_mirror(i)] for i in board.pieces(chess.BISHOP, chess.BLACK))
    wQtv = sum(queens_table[i] for i in board.pieces(chess.QUEEN, chess.WHITE))
    bQtv = sum(queens_table[chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK))
    wKtv = sum(kings_table[i] for i in board.pieces(chess.KING, chess.WHITE))
    bKtv = sum(kings_table[chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK))
    pieces = pieces + wptv + wRtv + wNtv + wBtv + wQtv + wKtv - (bptv + bRtv + bNtv + bBtv + bQtv + bKtv)
    global board_value
    board_value = pieces

    eval_time += time.time() - s
    return board_value


def eval_board_increment():
    if board.is_checkmate():
        if board.turn:
            return -99999
        else:
            return 99999

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    evaluation = board_value
    if board.turn:
        return evaluation
    else:
        return -evaluation


def update_eval(mov, side):
    global eval_time
    global board_value
    s = time.time()
    moving = board.piece_type_at(mov.from_square)

    # piece square tables
    if side:
        board_value = board_value - tables[moving - 1][mov.from_square]
        # update castling
        if (mov.from_square == chess.E1) and (mov.to_square == chess.G1):
            board_value = board_value - rooks_table[chess.H1]
            board_value = board_value + rooks_table[chess.F1]
        elif (mov.from_square == chess.E1) and (mov.to_square == chess.C1):
            board_value = board_value - rooks_table[chess.A1]
            board_value = board_value + rooks_table[chess.D1]
    else:
        board_value = board_value + tables[moving - 1][mov.from_square]
        # update castling
        if (mov.from_square == chess.E8) and (mov.to_square == chess.G8):
            board_value = board_value + rooks_table[chess.H8]
            board_value = board_value - rooks_table[chess.F8]
        elif (mov.from_square == chess.E8) and (mov.to_square == chess.C8):
            board_value = board_value + rooks_table[chess.A8]
            board_value = board_value - rooks_table[chess.D8]

    if side:
        board_value = board_value + tables[moving - 1][mov.to_square]
    else:
        board_value = board_value - tables[moving - 1][mov.to_square]

    # capturing
    if board.is_capture(mov):
        p_type = board.piece_at(mov.to_square)
        if p_type is not None:
            p_value = p_type.piece_type
        else:
            p_value = 1

        if side:
            board_value = board_value + piece_values[p_value - 1]
        else:
            board_value = board_value - piece_values[p_value - 1]

        # update promotion
    if mov.promotion is not None:
        if side:
            board_value = board_value + piece_values[mov.promotion - 1] - piece_values[moving - 1]
            board_value = board_value - tables[moving - 1][mov.to_square] \
                          + tables[mov.promotion - 1][mov.to_square]
        else:
            board_value = board_value - piece_values[mov.promotion - 1] + piece_values[moving - 1]
            board_value = board_value + tables[moving - 1][mov.to_square] \
                          - tables[mov.promotion - 1][mov.to_square]
    global eval_time
    eval_time += time.time() - s
    return mov


def eval_board():
    if board.is_checkmate():
        if board.turn:
            return -99999
        else:
            return 99999

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    pieces = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        if piece.color == chess.WHITE:
            pieces += pv[piece.piece_type]
        else:
            pieces -= pv[piece.piece_type]

    wptv = sum(pawn_table[i] for i in board.pieces(chess.PAWN, chess.WHITE))
    bptv = sum(pawn_table[chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK))
    wRtv = sum(rooks_table[i] for i in board.pieces(chess.ROOK, chess.WHITE))
    bRtv = sum(rooks_table[chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK))
    wNtv = sum(knights_table[i] for i in board.pieces(chess.KNIGHT, chess.WHITE))
    bNtv = sum(knights_table[chess.square_mirror(i)] for i in board.pieces(chess.KNIGHT, chess.BLACK))
    wBtv = sum(bishops_table[i] for i in board.pieces(chess.BISHOP, chess.WHITE))
    bBtv = sum(bishops_table[chess.square_mirror(i)] for i in board.pieces(chess.BISHOP, chess.BLACK))
    wQtv = sum(queens_table[i] for i in board.pieces(chess.QUEEN, chess.WHITE))
    bQtv = sum(queens_table[chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK))
    wKtv = sum(kings_table[i] for i in board.pieces(chess.KING, chess.WHITE))
    bKtv = sum(kings_table[chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK))
    pieces = pieces + wptv + wRtv + wNtv + wBtv + wQtv + wKtv - (bptv + bRtv + bNtv + bBtv + bQtv + bKtv)

    if board.turn:
        return pieces
    else:
        return -pieces


def make_move(mov):
    # update_eval(mov, board.turn)
    board.push(mov)

    return mov


def unmake_move():
    mov = board.pop()
    # update_eval(mov, not board.turn)

    return mov


def min_max_with_pruning(alpha, beta, depth_left, null_move):
    type = 'alpha'
    temp = probe_hash(depth_left, alpha, beta)

    # Hashtable check
    if temp != 'unknown' and should_use_hash_table:
        global used_trans_table_lookup
        used_trans_table_lookup += 1
        return temp
    global pos_evaluated

    pos_evaluated += 1

    # depth 0 start quiesce
    if depth_left <= 0:
        global quisce_time
        s = time.time()
        value = quiesce(alpha, beta)
        quisce_time += time.time() - s

        # value = eval_board()
        record_Hash(depth_left, value, 'exact')
        return value

    make_null_move(beta, depth_left)

    # depth >0 search all legal moves
    y = time.time()
    sorted_moves = sort_capture_moves(board.legal_moves)
    global sort_time
    sort_time += time.time() - y
    for move in sorted_moves:
        make_move(move)
        global remember_move
        remember_move = move
        current_score = -min_max_with_pruning(-beta, -alpha, depth_left - 1, not null_move)
        unmake_move()

        if current_score >= beta:
            record_Hash(depth_left, beta, 'beta')
            return beta

        if current_score > alpha:
            alpha = current_score
            type = 'exact'

    record_Hash(depth_left, alpha, type)
    return alpha


def make_null_move(beta, depth_left):
    # null move pruning todo not sure if working correctly
    if not board.is_check() and should_null_move and depth_left >= 3:
        board.turn = not board.turn
        reduce_depth = 2
        test = -min_max_with_pruning(-beta, -beta, depth_left - 1 - reduce_depth, False)
        board.turn = not board.turn
        if test >= beta:
            return test


def probe_hash(depth, alpha, beta):
    # return 'unknown'
    zob = chess.polyglot.zobrist_hash(board)
    if zob in trans_table.keys():
        entry = trans_table[zob]
        if entry.depth >= depth:
            if entry.flag == 'exact':
                return entry.score
            if entry.flag == 'alpha' and entry.score <= alpha:
                return alpha
            if entry.flag == 'beta' and entry.score >= beta:
                return beta
        else:
            global best_move
            best_move = remember_move

    return 'unknown'


def record_Hash(depth, val, hash_type):
    zob = chess.polyglot.zobrist_hash(board)
    global best_move
    trans_table[zob] = hash_entry(zob, depth, val, best_move, hash_type)


def quiesce(alpha, beta, q_depth=100):
    global quiesce_search
    quiesce_search += 1

    # dont check more captures if you are in check
    # if board.is_check():
    #    return min_max_with_pruning(alpha, beta, 1)

    current_score = eval_board()
    if current_score >= beta:
        return beta
    if alpha < current_score:
        alpha = current_score

    if q_depth == 0:
        return alpha
    st = time.time()
    sorted_captures = sort_capture_moves(board.legal_moves, False)
    global sort_time
    sort_time += time.time() - st

    for move in sorted_captures:

        make_move(move)
        board_score = -quiesce(-beta, -alpha, q_depth - 1)
        unmake_move()

        if board_score >= beta:
            return beta
        if board_score > alpha:
            alpha = board_score
    return alpha


t_get_piece = 0
t_capture_check = 0
make_lists = 0
check_and_append = 0
loop = 0


def sort_capture_moves(moves, min_max=True):
    global t_get_piece
    global t_capture_check
    global make_lists
    global check_and_append
    global loop
    la = time.time()
    rest = list()

    big = list()
    med = list()
    zero = list()
    negative = list()
    big_negative = list()
    make_lists += time.time() - la

    x = time.time()
    for c in moves:
        loop += time.time() - x
        x = time.time()
        a = board.is_capture(c)
        t_capture_check += time.time() - x
        if a:
            s = time.time()
            if True:
                if board.is_en_passant(c):
                    piece_type_end = 1
                else:
                    piece_type_end = board.piece_at(c.to_square).piece_type
            else:
                piece_end = board.piece_at(c.to_square)

                # piece_end is none if en passant capture
                if piece_end is None:
                    piece_type_end = 1
                else:
                    piece_type_end = piece_end.piece_type

            piece_type_start = board.piece_at(c.from_square).piece_type
            t_get_piece += time.time() - s

            c_t = time.time()
            if piece_type_end - piece_type_start >= 3:
                big.append(c)
            elif piece_type_end - piece_type_start >= 1:
                med.append(c)
            elif piece_type_end - piece_type_start == 0:
                zero.append(c)
            elif piece_type_end - piece_type_start <= -3:
                big_negative.append(c)
            else:
                negative.append(c)
            check_and_append += time.time() - c_t

        elif min_max:
            c_t = time.time()
            rest.append(c)
            check_and_append += time.time() - c_t

        x = time.time()
    sorted_captures = big + med + zero + rest + negative + big_negative
    return sorted_captures


best_moves = list()
best_moves_eval = list()


def select_move(depth):
    try:
        move = chess.polyglot.MemoryMappedReader("bookfish.bin").weighted_choice(board).move
        move_history.append(move.uci())
        print("book " + str(eval_board()))
        global best_engine_score
        best_engine_score = - eval_board()
        return move
    except:
        global trans_table, best_moves, best_moves_eval
        best_moves = list()
        best_moves_eval = list()
        found_best_move = chess.Move.null()
        best_value = -99999
        alpha = -100000
        beta = 100000
        moves = sort_capture_moves(board.legal_moves)
        trans_table.clear()
        t = "\nBlacks Turn: " + str(should_null_move)
        if board.turn:
            t = "\nWhites Turn: " + str(should_null_move)
        print(t)
        start_time = time.time()
        for i in range(1, depth):
            start_depth = time.time()
            should_print_time_check = time.time() - start_time > time_limit
            if not should_print_time_check:
                print("Searching depth " + str(i))

            draw_sideboard(surface)
            display_searching(surface)
            for move in moves:
                if time.time() - start_time > time_limit:
                    # print("\n \n TIME LIMIT REACHED \n \n")
                    break
                # draw_sideboard(surface)
                # display_searching(surface)
                make_move(move)
                s = time.time()
                found_board_value = -min_max_with_pruning(-beta, -alpha, i - 1, True)
                global min_max_time
                min_max_time += time.time() - s
                if found_board_value > best_value:
                    best_value = found_board_value
                    found_best_move = move
                if found_board_value > alpha:
                    alpha = found_board_value
                # z_hash = chess.polyglot.zobrist_hash(board)
                # trans_table[z_hash] = hash_entry(z_hash, depth, board_value, move, 'exact')
                unmake_move()
            if not should_print_time_check:
                print("took " + str(time.time() - start_depth) + "seconds at depth " + str(i) + " found " + str(
                    found_best_move.uci()))
                print("Searched " + str(pos_evaluated + quiesce_search) + " nodes\n")
                best_moves.append(found_best_move.uci())
                best_moves_eval.append(best_value)
        print(str((pos_evaluated + quiesce_search) / (time.time() - start_time)))
        print((time.time() - start_time))
        best_engine_score = - best_value
        move_history.append(found_best_move.uci())
        return found_best_move


def sort_moves():
    global trans_table
    move_list = list()
    for key in trans_table.keys():
        move_list.append((trans_table[key].move, trans_table[key].score))
    move_list.sort(key=lambda x: x[1], reverse=True)

    final_move = list()
    for m in move_list:
        final_move.append(m[0])
    return final_move


def select_square():
    col, row = pygame.mouse.get_pos()
    row = row // tilesize
    col = col // tilesize
    return row, col


def number_to_text(rank):
    if rank == 0:
        return "a"
    if rank == 1:
        return "b"
    if rank == 2:
        return "c"
    if rank == 3:
        return "d"
    if rank == 4:
        return "e"
    if rank == 5:
        return "f"
    if rank == 6:
        return "g"
    else:
        return "h"


def make_human_move(ps, ds):
    ps_row = 8 - ps[0]
    ps_col = number_to_text(ps[1])
    ds_row = 8 - ds[0]
    ds_col = number_to_text(ds[1])

    if (ps_row == 7 or ps_row == 1) and ds[1] > 7:
        if ps_row == 7:
            next_row = 8
        else:
            next_row = 0

        if ds[1] == 8:
            p = 'q'
        elif ds[1] == 9:
            p = 'r'
        elif ds[1] == 10:
            p = 'n'
        else:
            p = 'b'

        string = ps_col + str(ps_row) + ps_col + str(next_row) + p
    else:
        string = ps_col + str(ps_row) + ds_col + str(ds_row)

    if ps_col + str(ps_row) != ds_col + str(ds_row):
        move = chess.Move.from_uci(string)
        print(move)
        if move in board.legal_moves:
            make_move(move)
            # false = blacks turn
            return False
        else:
            return True
    else:
        return True


def draw_sideboard(surface):
    global draw_time
    s = time.time()
    pygame.draw.rect(surface, true_black, (8 * tilesize, 0 * tilesize, tilesize * 4, tilesize * 8))
    text = font.render("Positions Evaluated " + str(pos_evaluated), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 0.1 * tilesize + tilesize / 2)
    surface.blit(text, textRect)
    text = font.render("Quiesce Evaluated " + str(quiesce_search), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 0.4 * tilesize + tilesize / 2)
    surface.blit(text, textRect)

    text = font.render("Total Evaluated " + str(pos_evaluated + quiesce_search), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 0.7 * tilesize + tilesize / 2)
    surface.blit(text, textRect)

    text = font.render("Hashtable lookups " + str(used_trans_table_lookup), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 1 * tilesize + tilesize / 2)
    surface.blit(text, textRect)

    text = font.render("Hashtable Size  " + str(len(trans_table)), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 1.3 * tilesize + tilesize / 2)
    surface.blit(text, textRect)

    text = font.render("Evaluation " + str(eval_board() / 100), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 1.6 * tilesize + tilesize / 2)
    surface.blit(text, textRect)

    # text = font.render("Movelist " + str(move_history), True, white)
    # textRect = text.get_rect()
    # textRect.center = (9 * tilesize + tilesize / 2, 1.6 * tilesize + tilesize / 2)
    # surface.blit(text, textRect)

    promotion(surface)

    pygame.display.update()
    draw_time += time.time() - s


def promotion(surface):
    draw_piece(surface, 8, chess.Piece(chess.QUEEN, chess.WHITE), True)
    draw_piece(surface, 9, chess.Piece(chess.ROOK, chess.WHITE), True)
    draw_piece(surface, 10, chess.Piece(chess.KNIGHT, chess.WHITE), True)
    draw_piece(surface, 11, chess.Piece(chess.BISHOP, chess.WHITE), True)


def display_searching(surface):
    draw_sideboard(surface)
    text = font.render("Searching", True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 2 * tilesize + tilesize / 2)
    surface.blit(text, textRect)
    pygame.display.update()


def make_random_move():
    ml = list()
    for m in board.legal_moves:
        ml.append(m)

    rand = random.randrange(0, len(ml), 1)
    make_move(ml[rand])


def manual_game():
    global should_null_move
    should_null_move = False
    selected = False
    ps = None
    ds = None
    depth = 6
    playerColor = True
    random_moves = False
    eval_board_start()

    while True:

        while not board.is_checkmate():
            draw_board(surface)
            pygame.display.update()

            if playerColor:
                draw_sideboard(surface)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if not selected:
                            ps = select_square()
                            selected = True
                        else:
                            ds = select_square()
                            selected = False
                            playerColor = make_human_move(ps, ds)

                draw_board(surface)
                pygame.display.update()

            else:
                display_searching(surface)
                global pos_evaluated
                pos_evaluated = 0
                global quiesce_search
                quiesce_search = 0
                global used_trans_table_lookup
                used_trans_table_lookup = 0
                if random_moves:
                    make_random_move()
                else:
                    mov = select_move(depth)
                    make_move(mov)

                draw_sideboard(surface)
                draw_board(surface)
                pygame.display.update()
                playerColor = not playerColor

        draw_board(surface)
        pygame.display.update()


def stockfish_game(starting_string=False):
    global board
    depth = 20
    player_color = True

    engine = chess.engine.SimpleEngine.popen_uci(
        "C:/Users/Luca/PycharmProjects/chessaipythonchess/engines/stockfish_14_x64_avx2.exe")

    if starting_string:
        board = chess.Board("r1bqk1nr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    global board_value
    board_value = eval_board_start()

    while not board.is_game_over(claim_draw=True):
        draw_board(surface)
        pygame.display.update()
        display_searching(surface)
        global pos_evaluated
        pos_evaluated = 0
        global quiesce_search
        quiesce_search = 0
        global used_trans_table_lookup
        used_trans_table_lookup = 0

        if board.turn:
            mov = select_move(depth)
            print(mov)
            make_move(mov)
        else:
            engine_move = engine.play(board, chess.engine.Limit(0.000001))
            print(engine_move.move)
            make_move(engine_move.move)

        draw_sideboard(surface)
        draw_board(surface)
        pygame.display.update()
        player_color = not player_color

    print(board.fullmove_number)
    print("GAME ENDED")
    print("outcome")
    print(board.outcome().result())


def computer_game(starting_string=False):
    global board, should_null_move, time_limit
    depth = 5
    player_color = True

    if starting_string:
        board = chess.Board("1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - 0 1")
    global board_value
    board_value = eval_board_start()

    while not board.is_game_over(claim_draw=True):
        draw_board(surface)
        pygame.display.update()
        display_searching(surface)
        global pos_evaluated
        pos_evaluated = 0
        global quiesce_search
        quiesce_search = 0
        global used_trans_table_lookup
        used_trans_table_lookup = 0

        mov = select_move(depth)
        make_move(mov)

        draw_sideboard(surface)
        draw_board(surface)
        pygame.display.update()
        player_color = not player_color
        if board.turn:
            should_null_move = False
        else:
            should_null_move = False

    print("GAME ENDED")
    print("outcome")
    print(board.outcome().result())


def test_engine():
    positions = [
        "1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - 0 1",
        "3r1k2/4npp1/1ppr3p/p6P/P2PPPP1/1NR5/5K2/2R5 w - - 0 1",
        "2q1rr1k/3bbnnp/p2p1pp1/2pPp3/PpP1P1P1/1P2BNNP/2BQ1PRK/7R b - - 0 1",
        "rnbqkb1r/p3pppp/1p6/2ppP3/3N4/2P5/PPP1QPPP/R1B1KB1R w KQkq - 0 1",
        "r1b2rk1/2q1b1pp/p2ppn2/1p6/3QP3/1BN1B3/PPP3PP/R4RK1 w - - 0 1",
        "2r3k1/pppR1pp1/4p3/4P1P1/5P2/1P4K1/P1P5/8 w - - 0 1",
        "1nk1r1r1/pp2n1pp/4p3/q2pPp1N/b1pP1P2/B1P2R2/2P1B1PP/R2Q2K1 w - - 0 1",
        "4b3/p3kp2/6p1/3pP2p/2pP1P2/4K1P1/P3N2P/8 w - - 0 1",
        "2kr1bnr/pbpq4/2n1pp2/3p3p/3P1P1B/2N2N1Q/PPP3PP/2KR1B1R w - - 0 1",
        "3rr1k1/pp3pp1/1qn2np1/8/3p4/PP1R1P2/2P1NQPP/R1B3K1 b - - 0 1",
        "2r1nrk1/p2q1ppp/bp1p4/n1pPp3/P1P1P3/2PBB1N1/4QPPP/R4RK1 w - - 0 1",
        "r3r1k1/ppqb1ppp/8/4p1NQ/8/2P5/PP3PPP/R3R1K1 b - - 0 1",
        "r2q1rk1/4bppp/p2p4/2pP4/3pP3/3Q4/PP1B1PPP/R3R1K1 w - - 0 1",
        "rnb2r1k/pp2p2p/2pp2p1/q2P1p2/8/1Pb2NP1/PB2PPBP/R2Q1RK1 w - - 0 1",
        "2r3k1/1p2q1pp/2b1pr2/p1pp4/6Q1/1P1PP1R1/P1PN2PP/5RK1 w - - 0 1",
        "r1bqkb1r/4npp1/p1p4p/1p1pP1B1/8/1B6/PPPN1PPP/R2Q1RK1 w kq - 0 1",
        "r2q1rk1/1ppnbppp/p2p1nb1/3Pp3/2P1P1P1/2N2N1P/PPB1QP2/R1B2RK1 b - - 0 1",
        "r1bq1rk1/pp2ppbp/2np2p1/2n5/P3PP2/N1P2N2/1PB3PP/R1B1QRK1 b - - 0 1",
        "3rr3/2pq2pk/p2p1pnp/8/2QBPP2/1P6/P5PP/4RRK1 b - - 0 1",
        "r4k2/pb2bp1r/1p1qp2p/3pNp2/3P1P2/2N3P1/PPP1Q2P/2KRR3 w - - 0 1",
        "3rn2k/ppb2rpp/2ppqp2/5N2/2P1P3/1P5Q/PB3PPP/3RR1K1 w - - 0 1",
        "2r2rk1/1bqnbpp1/1p1ppn1p/pP6/N1P1P3/P2B1N1P/1B2QPP1/R2R2K1 b - - 0 1",
        "r1bqk2r/pp2bppp/2p5/3pP3/P2Q1P2/2N1B3/1PP3PP/R4RK1 b kq - 0 1",
        "r2qnrnk/p2b2b1/1p1p2pp/2pPpp2/1PP1P3/PRNBB3/3QNPPP/5RK1 w - - 0 1",
    ]
    solutions = ["Qd1+", "d5", "f5", "e6", "a4", "g6", "Nf6", "f5", "f5", "Ne5", "f4", "Bf5", "b4",
                 "Qd2 Qe1", "Qxg7+", "Ne4", "h5", "Nb3", "Rxe4", "g4", "Nh6", "Bxe4", "f6", "f4"]

    global board, board_value, should_null_move, time_limit, should_use_hash_table, quiesce_search, pos_evaluated, \
        used_trans_table_lookup

    depth = 30
    solved = 0
    stockfish = False
    should_null_move = True
    should_use_hash_table = True
    time_limit = 10

    null_hash_right = list()
    hash_right = list()
    none_right = list()

    # engine = chess.engine.SimpleEngine.popen_uci(
    # "C:/Users/Luca/PycharmProjects/chessaipythonchess/engines/stockfish_14_x64_avx2.exe")

    for i in range(24):
        movehistory = []
        board = chess.Board(positions[i])
        board_value = eval_board_start()

        quiesce_search = 0
        pos_evaluated = 0
        used_trans_table_lookup = 0
        draw_board(surface)
        pygame.display.update()

        if stockfish:
            engine_mov = engine.play(board, chess.engine.Limit(5))
            mov = engine_mov.move

        else:
            mov = select_move(depth)
        print("Move problem " + str(i + 1) + " " + board.san(mov) + " / Solution: " + solutions[
            i] + " uci move " + mov.uci())
        print(best_moves)
        print(best_moves_eval)

        if str(board.san(mov)) in str(solutions[i]):
            solved = solved + 1
            print("OK")
            null_hash_right.append(True)
        else:
            print("wrong")
            null_hash_right.append(False)

    print("Number of correct solved: " + str(solved))

    solved = 0
    should_null_move = False

    for i in range(24):
        movehistory = []
        board = chess.Board(positions[i])
        board_value = eval_board_start()

        quiesce_search = 0
        pos_evaluated = 0
        used_trans_table_lookup = 0
        draw_board(surface)
        pygame.display.update()

        mov = select_move(depth)
        print("Move problem " + str(i + 1) + " " + board.san(mov) + " / Solution: " + solutions[
            i] + " uci move " + mov.uci())
        print(best_moves)
        print(best_moves_eval)

        if str(board.san(mov)) in str(solutions[i]):
            solved = solved + 1
            print("OK")
            hash_right.append(True)
        else:
            print("wrong")
            hash_right.append(False)

    print("Number of correct solved: " + str(solved))

    solved = 0
    should_use_hash_table = False

    for i in range(24):
        movehistory = []
        board = chess.Board(positions[i])
        board_value = eval_board_start()

        quiesce_search = 0
        pos_evaluated = 0
        used_trans_table_lookup = 0
        draw_board(surface)
        pygame.display.update()

        mov = select_move(depth)
        print("Move problem " + str(i + 1) + " " + board.san(mov) + " / Solution: " + solutions[
            i] + " uci move " + mov.uci())
        print(best_moves)
        print(best_moves_eval)

        if str(board.san(mov)) in str(solutions[i]):
            solved = solved + 1
            print("OK")
            none_right.append(True)
        else:
            print("wrong")
            none_right.append(False)

    print("Number of correct solved: " + str(solved))

    print(null_hash_right)
    print(hash_right)
    print(none_right)


def print_stats():
    s = time.time()
    print("moves")
    print(board.fullmove_number)
    print("draw screen")
    print(draw_time)
    print("minmax")
    print(min_max_time)
    print("quisce")
    print(quisce_time)
    print("sort")
    print(sort_time)
    print("eval")
    print(eval_time)
    print("capture check")
    print(t_capture_check)
    print("get pieces")
    print(t_get_piece)
    print("make lists")
    print(make_lists)
    print("check and append")
    print(check_and_append)
    print("loop")
    print(loop)
    print("search added up")
    x = t_get_piece + t_capture_check + make_lists + check_and_append + loop
    print(x)
    print("diff")
    print(100 - 100 / sort_time * x)
    print("total")
    print(time.time() - s)


if __name__ == '__main__':
    test_engine()
