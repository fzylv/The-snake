import tkinter
import random
import pygame
from tkinter import simpledialog
from PIL import Image, ImageTk

pygame.mixer.init()
eating_sound = pygame.mixer.Sound("eat.mp3")

# python constants are in all caps LOL
ROWS = 25
COLS = 25
TILE_SIZE = 25

WINDOW_WIDH = TILE_SIZE * ROWS
WINDOW_HEIGHT = TILE_SIZE * COLS


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


window = tkinter.Tk()
window.title("Snake Game")
window.resizable(False, False)

canvas = tkinter.Canvas(window, bg="black", width=WINDOW_WIDH,height=WINDOW_HEIGHT, borderwidth=0, highlightthickness=0)
canvas.pack()
window.update()


# center the game window
window_widh = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width/2) - (window_widh/2))
window_y = int((screen_height/2) - (window_height/2))

window.geometry(f"{window_widh}x{window_height}+{window_x}+{window_y}")

snake = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)  # the snake
food = Tile(10 * TILE_SIZE, 10 * TILE_SIZE)
snake_body = []
velocityX = 0
velocityY = 0
game_over = False
score = 0
draw_loop = None
player_name = ""
player_name = simpledialog.askstring("Player Name", "Enter your name:", parent=window)


def load_high_scores():
    try:
        with open("high_scores.txt", "r") as file:
            scores = []
            for line in file:
                name, score = line.strip().split(",")
                scores.append((name, int(score)))
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores
    except FileNotFoundError:
        return []


def save_high_scores(scores):
    with open("high_scores.txt", "w") as file:
        for name, score in scores:
            file.write(f"{name},{score}\n")


def get_high_score(scores, name):
    for n, s in scores:
        if n == name:
            return s
    return 0


high_scores = load_high_scores()
high_score = get_high_score(high_scores, player_name)


def change_direction(e):
    global velocityX, velocityY

    if game_over:
        return

    if ((e.keysym == "Up" or e.keysym == "w") and velocityY != 1):
        velocityX = 0
        velocityY = -1
    elif ((e.keysym == "Down" or e.keysym == "s") and velocityY != -1):
        velocityX = 0
        velocityY = 1
    elif ((e.keysym == "Left" or e.keysym == "a") and velocityX != 1):
        velocityX = -1
        velocityY = 0
    elif ((e.keysym == "Right" or e.keysym == "d") and velocityX != -1):
        velocityX = 1
        velocityY = 0


def restart_game():
    global snake, food, snake_body, velocityX, velocityY, game_over, score, draw_loop

    if draw_loop is not None:
        window.after_cancel(draw_loop)

    snake.x = 5 * TILE_SIZE
    snake.y = 5 * TILE_SIZE
    food.x = 10 * TILE_SIZE
    food.y = 10 * TILE_SIZE
    snake_body = []
    velocityX = 0
    velocityY = 0
    game_over = False
    score = 0

    draw()


def move():
    global snake, game_over, food, snake_body, score, high_score, high_scores, player_name

    if game_over:
        return

    if snake.x < 0 or snake.x >= WINDOW_WIDH or snake.y < 0 or snake.y >= WINDOW_HEIGHT:
        game_over = True
    else:
        for tile in snake_body:
            if snake.x == tile.x and snake.y == tile.y:
                game_over = True

    if game_over:
        if score > high_score:
            high_score = score
        high_scores = update_high_scores(high_scores, player_name, score)
        save_high_scores(high_scores)
        return

    if snake.x == food.x and snake.y == food.y:
        snake_body.append(Tile(food.x, food.y))
        food.x = random.randint(0, COLS - 1) * TILE_SIZE
        food.y = random.randint(0, ROWS - 1) * TILE_SIZE
        score += 1
        eating_sound.play()

    for i in range(len(snake_body) - 1, -1, -1):
        tile = snake_body[i]
        if i == 0:
            tile.x = snake.x
            tile.y = snake.y
        else:
            prev_tile = snake_body[i - 1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y

    snake.x += velocityX * TILE_SIZE
    snake.y += velocityY * TILE_SIZE


def update_high_scores(scores, name, new_score):
    updated = False
    for i, (n, s) in enumerate(scores):
        if n == name:
            if new_score > s:
                scores[i] = (name, new_score)
            updated = True
            break
    if not updated:
        scores.append((name, new_score))
    return scores


def draw():
    global snake, food, snake_body, game_over, score, draw_loop, high_score
    move()

    canvas.delete("all")

    canvas.create_rectangle(food.x, food.y, food.x + TILE_SIZE, food.y + TILE_SIZE, fill="#FFFDD0")

    canvas.create_rectangle(snake.x, snake.y, snake.x + TILE_SIZE, snake.y + TILE_SIZE, fill="#CCCCFF")

    for tile in snake_body:
        canvas.create_rectangle(tile.x, tile.y, tile.x + TILE_SIZE, tile.y + TILE_SIZE, fill="#CCCCFF")

    if game_over:
        canvas.create_text(WINDOW_WIDH / 2, WINDOW_HEIGHT / 2 - 80, font=("Arial", 24, "bold"), text=f"Game Over! Score: {score}", fill="#CCCCFF")

        top_scores = load_high_scores()[:5]
        y_offset = WINDOW_HEIGHT / 2 - 40
        canvas.create_text(WINDOW_WIDH / 2, y_offset, font=("Arial", 18, "bold"), text="Leaderboard:", fill="#FFFDD0") 

        for i, (name, top_score) in enumerate(top_scores):
            y_offset += 25
            canvas.create_text(WINDOW_WIDH / 2, y_offset, font=("Arial", 14), text=f"{i+1}. {name}: {top_score}", fill="#FFFFFF")

    else:
        canvas.create_text(60, 20, font=("Arial", 14, "bold"), text=f"Score: {score}", fill="#FFFFFF")

    draw_loop = window.after(100, draw)


draw()

window.bind("<KeyRelease>", change_direction)
window.bind("<space>", lambda e: restart_game())
window.mainloop()
