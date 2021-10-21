import operator

import chess
import chess.svg
import chess.polyglot
import pygame

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
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

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


def draw_piece(surface, square, piece):
    col = square % 8
    row = square // 8
    #  print(str(row) + str(col) + str(piece.color))

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


def min_max_with_pruning(alpha, beta, depth_left):
    type = 'alpha'
    temp = probe_hash(depth_left, alpha, beta)
    if temp != 'unknown':
        global used_trans_table_lookup
        used_trans_table_lookup += 1
        return temp
    global pos_evaluated
    pos_evaluated += 1
    if depth_left == 0:
        record_Hash(depth_left, alpha, 'exact')
        return quiesce(alpha, beta, 0)
    for move in board.legal_moves:
        board.push(move)
        global remember_move
        remember_move = move
        current_score = -min_max_with_pruning(-beta, -alpha, depth_left - 1)
        board.pop()
        if current_score >= beta:
            record_Hash(depth_left, beta, 'beta')
            return current_score
        if current_score > alpha:
            alpha = current_score
            type = 'exact'

    record_Hash(depth_left, alpha, type)
    return alpha


def probe_hash(depth, alpha, beta):
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
    else:
        return 'unknown'


def record_Hash(depth, val, hash_type):
    zob = chess.polyglot.zobrist_hash(board)
    global best_move
    trans_table[zob] = hash_entry(zob, depth, val, best_move, hash_type)


def quiesce(alpha, beta, local_quiesce):
    local_quiesce += 1
    if local_quiesce > 10:
        return beta
    global quiesce_search
    quiesce_search += 1
    current_score = eval_board()
    if current_score >= beta:
        return beta
    if alpha < current_score:
        alpha = current_score

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            board_score = -quiesce(-beta, -alpha, local_quiesce)
            board.pop()

            if board_score >= beta:
                return beta
            if board_score > alpha:
                alpha = board_score
    return alpha


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
        best_move = chess.Move.null()
        best_value = -99999
        alpha = -100000
        beta = 100000
        moves = board.legal_moves

        for i in range(0, depth + 2):
            start_time = time.time()
            print("\n Searching depth " + str(i))
            trans_table.clear()
            draw_sideboard(surface)
            display_searching(surface)
            for move in moves:
                draw_sideboard(surface)
                display_searching(surface)
                board.push(move)
                board_value = -min_max_with_pruning(-beta, -alpha, depth - 1)
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
                if board_value > alpha:
                    alpha = board_value
                z_hash = chess.polyglot.zobrist_hash(board)
                trans_table[z_hash] = hash_entry(z_hash, depth, board_value, move, 'exact')
                board.pop()
            print("took " + str(time.time() - start_time) + "seconds at depth " + str(i))


        best_engine_score = - best_value
        move_history.append(best_move.uci())
        return best_move


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


def make_move(ps, ds):
    ps_row = 8 - ps[0]
    ps_col = number_to_text(ps[1])
    ds_row = 8 - ds[0]
    ds_col = number_to_text(ds[1])
    string = ps_col + str(ps_row) + ds_col + str(ds_row)
    move = chess.Move.from_uci(string)
    print(move)
    if ps_col + str(ps_row) != ds_col + str(ds_row):
        if move in board.legal_moves:
            board.push(move)


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

    text = font.render("Evaluation " + str(best_engine_score / 100), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 1.3 * tilesize + tilesize / 2)
    surface.blit(text, textRect)


    text = font.render("Movelist " + str(move_history), True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 1.6 * tilesize + tilesize / 2)
    surface.blit(text, textRect)
    pygame.display.update()


def display_searching(surface):
    draw_sideboard(surface)
    text = font.render("Searching", True, white)
    textRect = text.get_rect()
    textRect.center = (9 * tilesize + tilesize / 2, 2 * tilesize + tilesize / 2)
    surface.blit(text, textRect)
    pygame.display.update()


if __name__ == '__main__':

    selected = False
    ps = None
    ds = None

    while True:

        while not board.is_checkmate():
            draw_board(surface)
            pygame.display.update()

            if board.turn:
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
                            make_move(ps, ds)

                draw_board(surface)
                pygame.display.update()
            else:
                display_searching(surface)
                pos_evaluated = 0
                quiesce_search = 0
                used_trans_table_lookup = 0
                mov = select_move(3)
                draw_sideboard(surface)
                board.push(mov)
                draw_board(surface)
                pygame.display.update()

        draw_board(surface)
        pygame.display.update()