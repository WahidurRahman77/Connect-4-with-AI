import numpy as np
import pygame
import sys
import math
import random

# --- Constants & Configuration ---
ROW_COUNT = 7    # <--- Board is now 7x7 to fix the rotation overflow!
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)      
YELLOW = (255, 255, 0) 
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
DARK_OVERLAY = (0, 0, 0, 200) 

# Piece Types
EMPTY = 0
HUMAN_PIECE = 1     
AI_PIECE = 2        
BLOCKER_PIECE = 3   

WINDOW_LENGTH = 4

# --- Board Functions ---
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    if piece == BLOCKER_PIECE:
        return False

    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

def tilt_board_90_degrees(board):
    new_board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    for r in range(ROW_COUNT):
        pieces = [board[r][c] for c in range(COLUMN_COUNT) if board[r][c] != 0]
        new_col = (ROW_COUNT - 1) - r 
        curr_row = 0 
        for piece in pieces:
            new_board[curr_row][new_col] = piece
            curr_row += 1 
    return new_board

# --- Minimax AI ---
def evaluate_window(window, piece):
    score = 0
    opp_piece = HUMAN_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4: score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1: score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2: score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1: score -= 4
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score

def is_terminal_node(board):
    return winning_move(board, HUMAN_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE): return (None, 10000000)
            elif winning_move(board, HUMAN_PIECE): return (None, -10000000)
            else: return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta: break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, HUMAN_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta: break
        return best_col, value

# --- Pygame Visuals & UI ---
def draw_board(board, screen):
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE)) 
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] != EMPTY:
                color = BLACK
                if board[r][c] == HUMAN_PIECE: color = RED
                elif board[r][c] == AI_PIECE: color = YELLOW
                elif board[r][c] == BLOCKER_PIECE: color = WHITE
                pygame.draw.circle(screen, color, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def main_menu(screen):
    font = pygame.font.SysFont("monospace", 40)
    title_font = pygame.font.SysFont("monospace", 50, bold=True)
    while True:
        screen.fill(BLACK)
        title = title_font.render("AI CONNECT FOUR", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        subtitle = font.render("Select Difficulty", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 160))

        easy_btn = pygame.Rect(WIDTH//2 - 100, 250, 200, 60)
        med_btn = pygame.Rect(WIDTH//2 - 100, 350, 200, 60)
        hard_btn = pygame.Rect(WIDTH//2 - 100, 450, 200, 60)

        pygame.draw.rect(screen, BLUE, easy_btn)
        pygame.draw.rect(screen, BLUE, med_btn)
        pygame.draw.rect(screen, RED, hard_btn) 

        screen.blit(font.render("EASY", True, WHITE), (easy_btn.x + 50, easy_btn.y + 10))
        screen.blit(font.render("MEDIUM", True, WHITE), (med_btn.x + 30, med_btn.y + 10))
        screen.blit(font.render("HARD", True, WHITE), (hard_btn.x + 50, hard_btn.y + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_btn.collidepoint(event.pos): return 'EASY'
                if med_btn.collidepoint(event.pos): return 'MEDIUM'
                if hard_btn.collidepoint(event.pos): return 'HARD'

# --- Main Execution Loop ---
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("AI Connect 4 - Project")
myfont = pygame.font.SysFont("monospace", 20)
win_font = pygame.font.SysFont("monospace", 40, bold=True)

# Outer Application Loop
while True:
    DIFFICULTY = main_menu(screen)

    # Initialize Game Variables
    AI_MISTAKE_PROBABILITY = 0
    if DIFFICULTY == 'EASY':
        HUMAN_BLOCKERS = 0
        AI_BLOCKERS = 0
        AI_MISTAKE_PROBABILITY = 0.80 
    elif DIFFICULTY == 'MEDIUM':
        HUMAN_BLOCKERS = 1
        AI_BLOCKERS = 1
        AI_MISTAKE_PROBABILITY = 0.60 
    elif DIFFICULTY == 'HARD':
        HUMAN_BLOCKERS = 3
        AI_BLOCKERS = 3
        AI_MISTAKE_PROBABILITY = 0.50 

    board = create_board()
    draw_board(board, screen)

    game_over = False
    turn = 0 
    TOTAL_MOVES = 0
    HAS_TILTED = False
    selected_piece = HUMAN_PIECE 
    game_result_text = ""

    # Gameplay Loop
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and HUMAN_BLOCKERS > 0:
                    selected_piece = BLOCKER_PIECE if selected_piece == HUMAN_PIECE else HUMAN_PIECE

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    color = RED if selected_piece == HUMAN_PIECE else WHITE
                    pygame.draw.circle(screen, color, (posx, int(SQUARESIZE/2)), RADIUS)
                
                status_text = f"{DIFFICULTY} | Blocker: {HUMAN_BLOCKERS} | Current: {'BLOCKER' if selected_piece == BLOCKER_PIECE else 'NORMAL'}"
                label = myfont.render(status_text, 1, WHITE)
                screen.blit(label, (10, 20))
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                
                if event.button == 3 and HUMAN_BLOCKERS > 0:
                    selected_piece = BLOCKER_PIECE if selected_piece == HUMAN_PIECE else HUMAN_PIECE
                    pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=event.pos)) 
                    continue
                    
                if turn == 0 and event.button == 1: 
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        
                        if selected_piece == BLOCKER_PIECE:
                            drop_piece(board, row, col, BLOCKER_PIECE)
                            HUMAN_BLOCKERS -= 1
                            if HUMAN_BLOCKERS == 0: selected_piece = HUMAN_PIECE 
                        else:
                            drop_piece(board, row, col, HUMAN_PIECE)
                            
                        TOTAL_MOVES += 1
                        turn += 1
                        turn = turn % 2
                        draw_board(board, screen)
                        
                        if winning_move(board, HUMAN_PIECE):
                            game_result_text = "You Win!"
                            game_over = True
                        elif len(get_valid_locations(board)) == 0:
                            game_result_text = "Game Drawn!"
                            game_over = True

        # AI Turn
        if turn == 1 and not game_over:
            pygame.time.wait(500)
            valid_locations = get_valid_locations(board)
            
            if random.random() < AI_MISTAKE_PROBABILITY:
                col = random.choice(valid_locations) 
            else:
                col, minimax_score = minimax(board, 5, -math.inf, math.inf, True) 
            
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                
                if AI_BLOCKERS > 0 and random.random() < 0.15:
                    drop_piece(board, row, col, BLOCKER_PIECE)
                    AI_BLOCKERS -= 1
                else:
                    drop_piece(board, row, col, AI_PIECE)
                    
                TOTAL_MOVES += 1    
                draw_board(board, screen)
                turn += 1
                turn = turn % 2
                
                if winning_move(board, AI_PIECE):
                    game_result_text = "AI Wins!"
                    game_over = True
                elif len(get_valid_locations(board)) == 0:
                    game_result_text = "Game Drawn!"
                    game_over = True

        # THE 90 DEGREE GRAVITY TILT TRIGGER
        if DIFFICULTY == 'HARD' and TOTAL_MOVES == 14 and not HAS_TILTED and not game_over:
            pygame.time.wait(1000) 
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            warning = win_font.render("90 DEGREE TILT!", 1, ORANGE)
            screen.blit(warning, (WIDTH//5, 10))
            pygame.display.update()
            pygame.time.wait(1500)
            
            board = tilt_board_90_degrees(board)
            HAS_TILTED = True
            draw_board(board, screen)
            
            if winning_move(board, HUMAN_PIECE):
                game_result_text = "You Win by Tilt!"
                game_over = True
            elif winning_move(board, AI_PIECE):
                game_result_text = "AI Wins by Tilt!"
                game_over = True
            elif len(get_valid_locations(board)) == 0:
                game_result_text = "Game Drawn!"
                game_over = True

    # --- Game Over Screen ---
    if game_over:
        # Create a dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY)
        screen.blit(overlay, (0, 0))

        # Render Result Text
        result_color = YELLOW if "AI" in game_result_text else (RED if "Win" in game_result_text else WHITE)
        label = win_font.render(game_result_text, True, result_color)
        screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//3))

        # Create Home Button
        home_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 60)
        pygame.draw.rect(screen, RED, home_btn)
        home_text = win_font.render("HOME", True, WHITE)
        screen.blit(home_text, (home_btn.x + 55, home_btn.y + 10))

        pygame.display.update()

        # Wait for user to click HOME or Quit
        waiting_for_home = True
        while waiting_for_home:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if home_btn.collidepoint(event.pos):
                        waiting_for_home = False