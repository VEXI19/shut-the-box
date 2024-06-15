import pygame
import random
import socket
import threading
import string
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
FPS = 30

# Server connection
SERVER = '127.0.0.1'
PORT = 65432

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def send_message(message):
    client.send(message.encode())

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()
            print(message)
        except:
            print("An error occurred!")
            client.close()
            break

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shut the Box")

# Font
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Generate game code
def generate_game_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Tile class
class Tile:
    def __init__(self, number, x, y, width, height):
        self.number = number
        self.rect = pygame.Rect(x, y, width, height)
        self.flipped = False
        self.permanently_flipped = False

    def draw(self, screen):
        if self.permanently_flipped:
            color = GREY
        elif self.flipped:
            color = RED
        else:
            color = GREEN
        pygame.draw.rect(screen, color, self.rect)
        text = font.render(str(self.number), True, WHITE if self.permanently_flipped else BLACK)
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))

    def flip(self):
        if not self.permanently_flipped:
            self.flipped = not self.flipped

    def set_permanently_flipped(self):
        self.permanently_flipped = True

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and not self.permanently_flipped

# Firework particle class
class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        for _ in range(100):
            speed = random.uniform(1, 3)
            angle = random.uniform(0, 2 * math.pi)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            self.particles.append([self.x, self.y, dx, dy, random.choice([RED, GREEN, BLUE])])

    def update(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.99
            p[3] *= 0.99

    def draw(self, screen):
        for p in self.particles:
            pygame.draw.circle(screen, p[4], (int(p[0]), int(p[1])), 3)

# Create tiles for player 1
tiles_player1 = []
tile_width, tile_height = 80, 100
spacing = 10
start_x = 50
start_y = 100

for i in range(9):
    x = start_x + i * (tile_width + spacing)
    y = start_y
    tile = Tile(i + 1, x, y, tile_width, tile_height)
    tiles_player1.append(tile)

# Create tiles for player 2
tiles_player2 = []
start_y_player2 = SCREEN_HEIGHT - (start_y + tile_height)

for i in range(9):
    x = start_x + i * (tile_width + spacing)
    y = start_y_player2
    tile = Tile(i + 1, x, y, tile_width, tile_height)
    tiles_player2.append(tile)

# Roll dice function
def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)

# Screens
START_SCREEN = 'start'
GAME_SCREEN = 'game'
current_screen = START_SCREEN

# Game code
game_code = ""

# Text input for join game
input_box = pygame.Rect(400, 200, 140, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
done = False

# Load background image
background_image = pygame.image.load('background.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Main game loop
running = True
clock = pygame.time.Clock()
dice = (0, 0)
message = "Press ROLL to roll the dice"
rolled_sum = 0
selection_message = ""
fireworks = []
player_turn = 1

while running:
    screen.blit(background_image, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if current_screen == START_SCREEN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if create_game_button.collidepoint(event.pos):
                    current_screen = GAME_SCREEN
                    game_code = generate_game_code()
                elif join_game_button.collidepoint(event.pos):
                    send_message(f"join_game {text}")
                    text = ''
                elif input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        send_message(f"join_game {text}")
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        
        elif current_screen == GAME_SCREEN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if roll_button.collidepoint(pos):
                    dice = roll_dice()
                    rolled_sum = dice[0] + dice[1]
                    message = f"Dice: {dice[0]} + {dice[1]} = {rolled_sum}"
                    send_message(message)
                    selection_message = ""
                    for tile in (tiles_player1 if player_turn == 1 else tiles_player2):
                        if not tile.permanently_flipped:
                            tile.flipped = False  # Reset flipped state for all tiles that are not permanently flipped
                elif confirm_button.collidepoint(pos):
                    tiles = tiles_player1 if player_turn == 1 else tiles_player2
                    total_selected = sum(tile.number for tile in tiles if tile.flipped)
                    if (total_selected == rolled_sum or
                        ((dice[0] == 1 or dice[1] == 1) and total_selected == 1)):
                        for tile in tiles:
                            if tile.flipped:
                                tile.set_permanently_flipped()
                                tile.flipped = False
                        selection_message = f"Player {player_turn} Selection Confirmed"
                        if all(tile.permanently_flipped for tile in tiles):
                            fireworks.append(Firework(SCREEN_WIDTH // 4 if player_turn == 1 else 3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
                    else:
                        selection_message = f"Player {player_turn} Incorrect Selection"
                    player_turn = 2 if player_turn == 1 else 1
                else:
                    for tile in (tiles_player1 if player_turn == 1 else tiles_player2):
                        if tile.is_clicked(pos):
                            tile.flip()
                            send_message(f"Tile {tile.number} {'flipped' if tile.flipped else 'unflipped'}")

    if current_screen == START_SCREEN:
        # Draw start screen
        create_game_button = pygame.Rect(400, 100, 200, 50)
        pygame.draw.rect(screen, GREEN, create_game_button)
        create_game_text = small_font.render("Create Game", True, BLACK)
        screen.blit(create_game_text, (create_game_button.x + 10, create_game_button.y + 10))

        join_game_button = pygame.Rect(400, 250, 200, 50)
        pygame.draw.rect(screen, BLUE, join_game_button)
        join_game_text = small_font.render("Join Game", True, BLACK)
        screen.blit(join_game_text, (join_game_button.x + 10, join_game_button.y + 10))

        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = small_font.render(text, True, BLACK)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        join_game_label = small_font.render("Enter Code:", True, BLACK)
        screen.blit(join_game_label, (input_box.x - 150, input_box.y + 5))

    elif current_screen == GAME_SCREEN:
        # Draw game screen
        for tile in tiles_player1:
            tile.draw(screen)
        for tile in tiles_player2:
            tile.draw(screen)
        
        # Draw dice roll result
        message_text = small_font.render(message, True, BLACK)
        screen.blit(message_text, (50, 300))

        # Draw selection message
        selection_message_text = small_font.render(selection_message, True, RED)
        screen.blit(selection_message_text, (50, 350))

        # Draw game code
        game_code_text = small_font.render(f"Game Code: {game_code}", True, BLACK)
        screen.blit(game_code_text, (SCREEN_WIDTH - 300, 50))

        # Draw roll dice button
        roll_button = pygame.Rect(400, 500, 200, 50)
        pygame.draw.rect(screen, GREEN, roll_button)
        roll_text = small_font.render("Roll Dice", True, BLACK)
        screen.blit(roll_text, (roll_button.x + 10, roll_button.y + 10))

        # Draw confirm selection button
        confirm_button = pygame.Rect(400, 600, 200, 50)
        pygame.draw.rect(screen, BLUE, confirm_button)
        confirm_text = small_font.render("Confirm", True, BLACK)
        screen.blit(confirm_text, (confirm_button.x + 10, confirm_button.y + 10))

        # Draw player turn
        player_turn_text = small_font.render(f"Player {player_turn}'s Turn", True, BLACK)
        screen.blit(player_turn_text, (50, 400))
    
    # Draw fireworks
    for firework in fireworks:
        firework.update()
        firework.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
client.close()
