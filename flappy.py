import pygame # Importerer Pygame-biblioteket for spillutvikling
import random  # Importerer random-biblioteket for å generere tilfeldige tall
import sys  # Importerer sys-biblioteket for systemrelaterte funksjoner
import sqlite3 # Importerer sqlite3-biblioteket for å jobbe med SQLite-databaser
import os # Importerer os-biblioteket for systemoperasjoner (filhåndtering)

# Start Pygame
pygame.init()

# Skjerminnstillinger
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simplified Flappy Bird")

# Farger
SKY_BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# Klokke
clock = pygame.time.Clock()
FPS = 30

# Fuglen
bird_position = [100, SCREEN_HEIGHT // 2]
bird_size = 20
bird_velocity = 0
gravity = 1
jump_force = -15

# Rør
pipe_width = 60
pipe_gap = 150
pipe_speed = 3
pipes = [{"x": SCREEN_WIDTH + x * 200, "height": random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)} for x in range(3)]

# Poeng
score = 0

# Oppsett av database
def setup_database(): # lager databasen og tabellen hvis de ikke finnes.
    conn = sqlite3.connect("highscore.db")  # Kobler til databasen
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscore (
            id INTEGER PRIMARY KEY,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def read_highscore(): #Henter highscore fra databasen
    conn = sqlite3.connect("highscore.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM highscore")
    result = cursor.fetchone()
    conn.close()
    if result[0] is None:
        return 0  # Returner 0 hvis ingen score er lagret
    return result[0]

def save_highscore(new_highscore): # Lagrer ny highscore hvis den er høyere enn eksisterende.
    conn = sqlite3.connect("highscore.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM highscore")
    current_highscore = cursor.fetchone()[0]
    if current_highscore is None or new_highscore > current_highscore:
        cursor.execute("INSERT INTO highscore (score) VALUES (?)", (new_highscore,))
        conn.commit()
    conn.close()

# Funksjon for å vise poeng og highscore
def display_score_and_highscore(): # Viser spillerens poeng og den lagrede highscoren.
    font = pygame.font.Font(None, 40)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    highscore_text = font.render(f"Highscore: {read_highscore()}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(highscore_text, (10, 50))

# Hovedspillfunksjon
def game():
    global bird_position, bird_velocity, score

    # Initialiser variabler
    bird_position[1] = SCREEN_HEIGHT // 2
    bird_velocity = 0
    score = 0
    pipes = [{"x": SCREEN_WIDTH + x * 200, "height": random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)} for x in range(3)]

    running = True
    while running:
        # Håndter brukerhandlinger
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_velocity = jump_force

        # Oppdater fuglens posisjon
        bird_velocity += gravity
        bird_position[1] += bird_velocity

        # Flytt rør og sjekk poeng
        for pipe in pipes:
            pipe["x"] -= pipe_speed
            if pipe["x"] + pipe_width < bird_position[0] and not pipe.get("passed", False):
                score += 1
                pipe["passed"] = True
            if pipe["x"] + pipe_width < 0:
                pipe["x"] = SCREEN_WIDTH
                pipe["height"] = random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)
                pipe["passed"] = False

        # Kollisjonsdeteksjon
        for pipe in pipes:
            if (bird_position[0] + bird_size > pipe["x"] and bird_position[0] < pipe["x"] + pipe_width and
                (bird_position[1] < pipe["height"] or bird_position[1] + bird_size > pipe["height"] + pipe_gap)):
                running = False
        if bird_position[1] <= 0 or bird_position[1] >= SCREEN_HEIGHT:
            running = False

        # Tegn bakgrunn, fugl, rør og poeng
        screen.fill(SKY_BLUE)
        pygame.draw.circle(screen, YELLOW, (bird_position[0], int(bird_position[1])), bird_size)
        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe["x"], 0, pipe_width, pipe["height"]))
            pygame.draw.rect(screen, GREEN, (pipe["x"], pipe["height"] + pipe_gap, pipe_width, SCREEN_HEIGHT))
        display_score_and_highscore()

        # Oppdater skjermen
        pygame.display.flip()
        clock.tick(FPS)

    # Håndter highscore
    highscore = read_highscore()
    if score > highscore:
        save_highscore(score)

    # Game Over-meny
    game_over_menu()

# Game Over-meny
def game_over_menu(): # Viser menyen for Game Over."""
    font = pygame.font.Font(None, 50)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    play_again_text = font.render("Press R to Restart", True, (255, 255, 255))
    quit_text = font.render("Press Q to Quit", True, (255, 255, 255))

    screen.fill(SKY_BLUE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart spillet
                    game()
                if event.key == pygame.K_q:  # Avslutt spillet
                    pygame.quit()
                    sys.exit()

# Sett opp databasen før spillet starter
setup_database()

# Start spillet
game()
