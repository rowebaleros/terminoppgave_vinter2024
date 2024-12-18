import pygame # Importerer Pygame-biblioteket for spillutvikling
import random  # Importerer random-biblioteket for å generere tilfeldige tall
import sys  # Importerer sys-biblioteket for systemrelaterte funksjoner
import sqlite3 # Importerer sqlite3-biblioteket for å jobbe med SQLite-databaser
import os # Importerer os-biblioteket for systemoperasjoner (filhåndtering)

# Start Pygame
pygame.init()

# Skjerminnstillinger
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Oppretter spillvinduet med spesifiserte dimensjoner
pygame.display.set_caption("Simplified Flappy Bird")  # Setter tittelen på vindue

# Farger
SKY_BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# Klokke
clock = pygame.time.Clock()
FPS = 30

# Fuglen
bird_position = [100, SCREEN_HEIGHT // 2] #plassering av fuglen på skjermen
bird_size = 20 # fuglens størrelse
bird_velocity = 0
gravity = 1 # hvor hard gravitasjonen får fuglen til å falle
jump_force = -10 # hvor høyt/hardt fuglen hopper per klikk

# Rør
pipe_width = 60
pipe_gap = 150
pipe_speed = 3
pipes = [{"x": SCREEN_WIDTH + x * 200, "height": random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)} for x in range(3)] # hvor mange rør det vil komme i tilfeldige høyder

# Poeng
score = 0

# Oppsett av database
def setup_database(): # lager databasen og tabellen hvis de ikke finnes.
    conn = sqlite3.connect("highscore.db") # kobler til SQLite-databasen (eller opprett den hvis den ikke finnes)
    cursor = conn.cursor() # lager en cursor for å utføre SQL-kommandoer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscore (
            id INTEGER PRIMARY KEY,
            score INTEGER
        )
    """) # lager en tabell hvis ikke du har en allerede
    conn.commit() # lagrer endringer i databasen
    conn.close() # Lukk tilkoblingen til databasen

def read_highscore(): #Henter highscore fra databasen
    conn = sqlite3.connect("highscore.db") # Åpner tilkobling til databasen
    cursor = conn.cursor() # Oppretter en cursor
    cursor.execute("SELECT MAX(score) FROM highscore")
    result = cursor.fetchone() # Henter første rad (resultatet)
    conn.close() # lukker tilkoblingen
    if result[0] is None:
        return 0  # returner 0 hvis ingen score er lagret
    return result[0] # returnerer den høyeste scoren som ble funnet

def save_highscore(new_highscore):  # Funksjonen lagrer en ny highscore hvis den er høyere enn eksisterende highscore.
    conn = sqlite3.connect("highscore.db")  # Oppretter eller åpner en tilkobling til databasen "highscore.db".
    # Hvis databasen ikke finnes, opprettes den automatisk.
    cursor = conn.cursor()  # Oppretter en cursor, som er et objekt som lar oss utføre SQL-spørringer mot databasen.
    cursor.execute("SELECT MAX(score) FROM highscore")  # Utfører en SQL-spørring for å hente den høyeste verdien 
    # (MAX) i kolonnen "score" fra tabellen "highscore".
    current_highscore = cursor.fetchone()[0]  # Henter resultatet fra spørringen som en tuple, og tar den første (og eneste) verdien.
    # Hvis tabellen er tom (ingen rader), returnerer spørringen None.
    
    if current_highscore is None or new_highscore > current_highscore:  # Sjekker to ting:
        # 1. Om det ikke finnes en highscore i databasen (current_highscore er None).
        # 2. Om den nye highscoren (new_highscore) er høyere enn den eksisterende highscoren.
        cursor.execute("INSERT INTO highscore (score) VALUES (?)", (new_highscore,))  # Setter inn den nye scoren som en ny rad i tabellen "highscore".
        conn.commit()  # Lagrer endringene i databasen. Det sikrer at den nye scoren blir permanent lagret.
    conn.close()  # Denne koden sørger for at den lukker forbindelsen til databasen for å unngå lås på databasen.

# Funksjon for å vise poeng og highscore
def display_score_and_highscore(): # Viser spillerens poeng og den lagrede highscoren.
    font = pygame.font.Font(None, 40) # gir teksten en font med størrelse 40
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # Oppretter en tekstoverflate som viser spillerens poengsum.
    # Teksten genereres i hvit farge (RGB: 255, 255, 255), er antialiasert (True for jevnere kanter), og bruker fonten definert tidligere.
    # Variabelen `score_text` lagrer denne overflaten, som senere kan tegnes på skjermen med `blit`.
    highscore_text = font.render(f"Highscore: {read_highscore()}", True, (255, 255, 255))  # Oppretter en tekstoverflate som viser spillerens høyeste poengsum (highscore).
    # `read_highscore()` kalles for å hente den lagrede høyeste scoren fra databasen. 
    # Teksten genereres i hvit farge (RGB: 255, 255, 255), har jevne kanter (antialiasing aktivert med True), og bruker den definerte fonten.
    # Variabelen `highscore_text` lagrer overflaten som senere kan vises på skjermen med `blit`.
    screen.blit(score_text, (10, 10)) # viser poeng på skjermen
    screen.blit(highscore_text, (10, 50)) # viser highscore på skjermen

# Hovedspillfunksjon
def game():  # Funksjonen kjører hovedspillet.
    global bird_position, bird_velocity, score  # Bruker globale variabler for å holde styr på fuglens posisjon, hastighet og poeng.

    # Initialiser variabler
    bird_position[1] = SCREEN_HEIGHT // 2  # Setter fuglens vertikale posisjon til midten av skjermen.
    bird_velocity = 0  # Setter fuglens hastighet til 0.
    score = 0  # Starter poengsummen på 0.
    pipes = [{"x": SCREEN_WIDTH + x * 200, "height": random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)} for x in range(3)]  
    # Oppretter en liste med tre rør, hvor hver får en tilfeldig høyde og plasseres med jevn avstand horisontalt.

    running = True  # Spillstatus for å holde spillet i gang.
    while running:  # Spillets hovedløkke.
        # Håndter brukerhandlinger
        for event in pygame.event.get():  # Går gjennom alle hendelser som skjer.
            if event.type == pygame.QUIT:  # Sjekker om spilleren lukker vinduet.
                pygame.quit()  # Avslutter Pygame.
                sys.exit()  # Avslutter programmet.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Sjekker om spilleren trykker på mellomromstasten.
                bird_velocity = jump_force  # Gir fuglen en hastighet oppover.

        # Oppdater fuglens posisjon
        bird_velocity += gravity  # Øker fuglens hastighet med tyngdekraften.
        bird_position[1] += bird_velocity  # Oppdaterer fuglens vertikale posisjon basert på hastigheten.

        # Flytt rør og sjekk poeng
        for pipe in pipes:  # Itererer gjennom hvert rør i listen.
            pipe["x"] -= pipe_speed  # Flytter rørene mot venstre med en gitt hastighet.
            if pipe["x"] + pipe_width < bird_position[0] and not pipe.get("passed", False):  
                # Sjekker om fuglen har passert røret og hvis røret ikke allerede er markert som passert.
                score += 1  # Øker poengsummen.
                pipe["passed"] = True  # Marker røret som passert.
            if pipe["x"] + pipe_width < 0:  # Sjekker om røret har forlatt skjermen til venstre.
                pipe["x"] = SCREEN_WIDTH  # Resetter røret til høyre side av skjermen.
                pipe["height"] = random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)  
                # Gir røret en ny tilfeldig høyde.
                pipe["passed"] = False  # Setter passert-status til False.

        # Kollisjonsdeteksjon
        for pipe in pipes:  # Itererer gjennom hvert rør for å sjekke kollisjon.
            if (bird_position[0] + bird_size > pipe["x"] and bird_position[0] < pipe["x"] + pipe_width and  
                # Sjekker om fuglen overlapper røret horisontalt.
                (bird_position[1] < pipe["height"] or bird_position[1] + bird_size > pipe["height"] + pipe_gap)):  
                # Sjekker om fuglen treffer toppen eller bunnen av røret.
                running = False  # Stopper spillet hvis det er kollisjon.
        if bird_position[1] <= 0 or bird_position[1] >= SCREEN_HEIGHT:  
            # Sjekker om fuglen går utenfor skjermens topp eller bunn.
            running = False  # Stopper spillet.

        # Tegn bakgrunn, fugl, rør og poeng
        screen.fill(SKY_BLUE)  # Fyller skjermen med en blå bakgrunn.
        pygame.draw.circle(screen, YELLOW, (bird_position[0], int(bird_position[1])), bird_size)  
        # Tegner fuglen som en gul sirkel.
        for pipe in pipes:  # Tegner hvert rør.
            pygame.draw.rect(screen, GREEN, (pipe["x"], 0, pipe_width, pipe["height"]))  
            # Tegner den øverste delen av røret.
            pygame.draw.rect(screen, GREEN, (pipe["x"], pipe["height"] + pipe_gap, pipe_width, SCREEN_HEIGHT))  
            # Tegner den nederste delen av røret.
        display_score_and_highscore()  # Viser poeng og highscore på skjermen.

        # Oppdater skjermen
        pygame.display.flip()  # Oppdaterer hele skjermen for å vise de nye tegningene.
        clock.tick(FPS)  # Regulerer hastigheten på spillet til en fast bildefrekvens.

    # Håndter highscore
    highscore = read_highscore()  # Leser den lagrede highscoren fra databasen.
    if score > highscore:  # Sjekker om spillerens poengsum er høyere enn highscoren.
        save_highscore(score)  # Lagre den nye highscoren hvis det er tilfelle.

    # Game Over-meny
    game_over_menu()  # Kaller funksjonen for Game Over-menyen.

# Game Over-meny
def game_over_menu():  # Funksjonen viser Game Over-menyen.
    font = pygame.font.Font(None, 50)  # Setter opp en font med størrelse 50.
    game_over_text = font.render("Game Over", True, (255, 0, 0))  # Lager en tekst som sier "Game Over" i rød farge.
    play_again_text = font.render("Press R to Restart", True, (255, 255, 255))  
    # Lager en tekst som instruerer spilleren om å trykke "R" for å starte på nytt.
    quit_text = font.render("Press Q to Quit", True, (255, 255, 255))  
    # Lager en tekst som instruerer spilleren om å trykke "Q" for å avslutte spillet.

    screen.fill(SKY_BLUE)  # Fyller skjermen med en blå bakgrunn.
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))  
    # Plasserer "Game Over"-teksten midt på skjermen.
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))  
    # Plasserer instruksjonen for å starte på nytt rett under "Game Over"-teksten.
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 50))  
    # Plasserer instruksjonen for å avslutte spillet under resten av tekstene.
    pygame.display.flip()  # Oppdaterer skjermen for å vise teksten.

    while True:  # Løkke som venter på spillerens handling.
        for event in pygame.event.get():  # Går gjennom alle hendelser som skjer.
            if event.type == pygame.QUIT:  # Sjekker om spilleren lukker vinduet.
                pygame.quit()  # Avslutter Pygame.
                sys.exit()  # Avslutter programmet.
            if event.type == pygame.KEYDOWN:  # Sjekker om en tast er trykket ned.
                if event.key == pygame.K_r:  # Sjekker om "R" er trykket.
                    game()  # Starter spillet på nytt.
                if event.key == pygame.K_q:  # Sjekker om "Q" er trykket.
                    pygame.quit()  # Avslutter Pygame.
                    sys.exit()  # Avslutter programmet.

# Sett opp databasen før spillet starter
setup_database()  # Kaller funksjonen for å sette opp databasen hvis den ikke allerede eksisterer.

# Start spillet
game()  # Starter hovedspillfunksjonen.
