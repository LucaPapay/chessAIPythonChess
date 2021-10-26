import operator

import chess
import chess.svg
import chess.polyglot
import pygame
import random

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
    chess.ROOK: 450,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
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
    draw_board_background(surface)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        draw_piece(surface, square, piece)


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

    return board_value


def eval_board():
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
    global board_value

    moving = board.piece_type_at(mov.from_square)
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

        # update material
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

    return mov


def make_move(mov):
    update_eval(mov, board.turn)
    board.push(mov)

    return mov


def unmake_move():
    mov = board.pop()
    update_eval(mov, not board.turn)

    return mov


def min_max_with_pruning(alpha, beta, depth_left):
    type = 'alpha'
    temp = probe_hash(depth_left, alpha, beta)

    # Hashtable check
    if temp != 'unknown':
        global used_trans_table_lookup
        used_trans_table_lookup += 1
        return temp
    global pos_evaluated

    pos_evaluated += 1

    # depth 0 start quiesce
    if depth_left == 0:
        value = quiesce(alpha, beta)
        # value = eval_board()
        record_Hash(depth_left, value, 'exact')
        return value

    # depth >0 search all legal moves
    sorted_moves = sort_capture_moves(board.legal_moves)
    for move in sorted_moves:
        make_move(move)
        global remember_move
        remember_move = move
        current_score = -min_max_with_pruning(-beta, -alpha, depth_left - 1)
        unmake_move()

        if current_score >= beta:
            record_Hash(depth_left, beta, 'beta')
            return beta

        if current_score > alpha:
            alpha = current_score
            type = 'exact'

    record_Hash(depth_left, alpha, type)
    return alpha


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


def quiesce(alpha, beta, q_depth=8):
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

    sorted_captures = sort_capture_moves(board.legal_moves, False)

    for move in sorted_captures:

        make_move(move)
        board_score = -quiesce(-beta, -alpha, q_depth - 1)
        unmake_move()

        if board_score >= beta:
            return beta
        if board_score > alpha:
            alpha = board_score
    return alpha


def sort_capture_moves(moves, min_max=True):
    rest = list()

    big = list()
    med = list()
    zero = list()
    negative = list()
    big_negative = list()

    for c in moves:
        if board.is_capture(c):

            piece_type_start = board.piece_at(c.from_square).piece_type

            piece_end = board.piece_at(c.to_square)

            # piece_end is none if en passant capture
            if piece_end is None:
                piece_type_end = 1
            else:
                piece_type_end = piece_end.piece_type

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
        elif min_max:
            rest.append(c)

    sorted_captures = big + med + zero + rest + negative + big_negative
    return sorted_captures


def select_move(depth):
    try:
        move = chess.polyglot.MemoryMappedReader("bookfish.bin").weighted_choice(board).move
        move_history.append(move.uci())
        print("book " + str(eval_board()))
        global best_engine_score
        best_engine_score = - eval_board()
        return move
    except:

        global trans_table
        found_best_move = chess.Move.null()
        best_value = -99999
        alpha = -100000
        beta = 100000
        moves = sort_capture_moves(board.legal_moves)
        trans_table.clear()
        t = "\nBlacks Turn:"
        if board.turn:
            t = "\nWhites Turn:"
        print(t)
        start_time = time.time()
        for i in range(1, depth):
            start_depth = time.time()
            print("Searching depth " + str(i))

            draw_sideboard(surface)
            display_searching(surface)
            for move in moves:
                # draw_sideboard(surface)
                # display_searching(surface)
                make_move(move)
                found_board_value = -min_max_with_pruning(-beta, -alpha, i - 1)
                if found_board_value > best_value:
                    best_value = found_board_value
                    found_best_move = move
                if found_board_value > alpha:
                    alpha = found_board_value
                # z_hash = chess.polyglot.zobrist_hash(board)
                # trans_table[z_hash] = hash_entry(z_hash, depth, board_value, move, 'exact')
                unmake_move()
            print("took " + str(time.time() - start_depth) + "seconds at depth " + str(i))
            print("Searched " + str(pos_evaluated + quiesce_search) + " nodes\n")

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

    text = font.render("Evaluation " + str(board_value / 100), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 1.6 * tilesize + tilesize / 2)
    surface.blit(text, textRect)

    # text = font.render("Movelist " + str(move_history), True, white)
    # textRect = text.get_rect()
    # textRect.center = (9 * tilesize + tilesize / 2, 1.6 * tilesize + tilesize / 2)
    # surface.blit(text, textRect)

    promotion(surface)

    pygame.display.update()


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
    selected = False
    ps = None
    ds = None
    depth = 5
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


def computer_game(starting_string=False):
    global board
    depth = 5
    player_color = True

    if starting_string:
        board = chess.Board("1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - 0 1")
    global board_value
    board_value = eval_board_start()

    while not board.is_game_over():
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

    print("GAME ENDED")
    print("outcome")
    print(board.outcome().result())


if __name__ == '__main__':
    computer_game()
