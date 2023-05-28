import sys
import random
import copy
from enum import Enum
import numpy as np
import pygame

from constants import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)


class TerminalState(Enum):
    PLAYER_1_WINS = 1
    PLAYER_2_WINS = 2
    DRAW = 0


class GameMode(Enum):
    AI = 'ai'
    PVP = 'pvp'


class Marker:
    def draw_cross(self, row, col):
        offset = SQ_SIZE / 4

        # desc line
        start_desc = (col * SQ_SIZE + offset, row * SQ_SIZE + offset)
        end_desc = (col * SQ_SIZE + SQ_SIZE - offset,
                    row * SQ_SIZE + SQ_SIZE - offset)
        pygame.draw.line(screen, CROSS_MARKER_COLOR, start_desc,
                         end_desc, CROSS_WIDTH)

        # asc line
        start_asc = (col * SQ_SIZE + SQ_SIZE -
                     offset, row * SQ_SIZE + offset)
        end_asc = (col * SQ_SIZE + offset,
                   row * SQ_SIZE + SQ_SIZE - offset)
        pygame.draw.line(screen, CROSS_MARKER_COLOR, start_asc,
                         end_asc, CROSS_WIDTH)

    def draw_circle(self, row, col):
        center = (col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2)
        pygame.draw.circle(screen, CIRCLE_MARKER_COLOR,
                           center, RADIUS, CIRCLE_WIDTH)


class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS), dtype=int)
        self.marker = Marker()
        self.marked_sqrs = 0
        self.clear()

    def terminal_state(self, show=False) -> TerminalState:
        '''
            @return 0 if there is no win
            @return 1 if player 1 wins
            @return 2 if player 2 wins 
        '''
        offset = SQ_SIZE // 4

        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRCLE_MARKER_COLOR if self.squares[0][col] else CROSS_MARKER_COLOR
                    sPos = ((col * SQ_SIZE) + (SQ_SIZE // 2), offset // 2)
                    ePos = ((col * SQ_SIZE) + (SQ_SIZE // 2),
                            HEIGHT - (offset // 2))
                    pygame.draw.line(screen, color, sPos, ePos, LINE_WIDTH)
                return TerminalState(self.squares[0][col])

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRCLE_MARKER_COLOR if self.squares[0][col] else CROSS_MARKER_COLOR
                    sPos = (offset // 2, (col * SQ_SIZE) - (SQ_SIZE // 2))
                    ePos = (WIDTH - (offset // 2), +
                            (col * SQ_SIZE) - (SQ_SIZE // 2))
                    pygame.draw.line(screen, color, sPos, ePos, LINE_WIDTH)
                return TerminalState(self.squares[row][0])

        # diagonal wins

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRCLE_MARKER_COLOR if self.squares[0][col] else CROSS_MARKER_COLOR
                sPos = (offset, offset)
                ePos = (WIDTH - (offset), HEIGHT - (offset))
                pygame.draw.line(screen, color, sPos, ePos, LINE_WIDTH)
            return TerminalState(self.squares[0][0])

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRCLE_MARKER_COLOR if self.squares[0][col] else CROSS_MARKER_COLOR
                sPos = (WIDTH - (offset), offset)
                ePos = (offset, HEIGHT - (offset))
                pygame.draw.line(screen, color, sPos, ePos, LINE_WIDTH)
            return TerminalState(self.squares[2][0])

        # no win
        return TerminalState.DRAW

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def is_sqr_empty(self, row, col):
        return self.squares[row][col] == 0

    def draw_marker(self, row, col, player):
        if player == 1:
            self.marker.draw_cross(row, col)
        elif player == 2:
            self.marker.draw_circle(row, col)

    def get_empty_sqrs(self):
        return [(row, col) for row in range(ROWS)
                for col in range(COLS) if self.is_sqr_empty(row, col)] or []

    def is_full(self):
        return self.marked_sqrs == 9

    def is_empty(self):
        return self.marked_sqrs == 0

    def clear(self):
        screen.fill(BG_COLOR)


class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    def random_move(self, board: Board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))
        return empty_sqrs[idx]

    def minimax(self, board: Board, maximizing: bool):
        state = board.terminal_state()
        if state == TerminalState.PLAYER_1_WINS:
            return 1, None
        elif state == TerminalState.PLAYER_2_WINS:
            return -1, None
        elif board.is_full():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                print(board)
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move
        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    def eval(self, board: Board):
        if self.level == 0:
            # random choice
            move = self.random_move(board)
            # self.level += 1
        else:
            # minimax
            _, move = self.minimax(board, False)

        return move


class Game:
    def __init__(self):
        self.player = 1
        self.board = Board()
        self.ai = AI(level=0)
        self.gamemode = GameMode.AI
        self.gameover = False
        self.show_lines()

    def show_lines(self):
        # Vertical
        pygame.draw.line(screen, LINE_COLOR, (SQ_SIZE, 0),
                         (SQ_SIZE, HEIGHT), LINE_WIDTH)

        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQ_SIZE, 0),
                         (WIDTH - SQ_SIZE, HEIGHT), LINE_WIDTH)

        # Horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQ_SIZE),
                         (WIDTH, SQ_SIZE), LINE_WIDTH)

        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQ_SIZE),
                         (WIDTH, HEIGHT - SQ_SIZE), LINE_WIDTH)

    def switch_turn(self):
        self.player = 2 if self.player == 1 else 1

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.board.draw_marker(row, col, self.player)
        self.switch_turn()

    def change_gamemode(self):
        self.gamemode = GameMode.AI if self.gamemode == GameMode.PVP else GameMode.PVP
        return self.gamemode

    def is_over(self):
        if self.board.terminal_state(show=True) != TerminalState.DRAW or self.board.is_full():
            return True
        else:
            return False

    def reset(self):
        self.__init__()


def main():
    game = Game()
    board = game.board
    ai = game.ai

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQ_SIZE
                col = pos[0] // SQ_SIZE

                if board.is_sqr_empty(row, col) and not game.gameover:
                    game.make_move(row, col)

                    if game.is_over():
                        game.gameover = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    game.change_gamemode()

                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai

        if game.gamemode == GameMode.AI and game.player == ai.player and not game.gameover:
            pygame.display.update()

            row, col = ai.eval(board)
            game.make_move(row, col)

            if game.is_over():
                game.gameover = True

        pygame.display.update()


main()
