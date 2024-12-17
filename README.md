# terminoppgave_vinter2024
#### her får du all info om min terminoppgave til vinteren 2024

## OBS:
#### kunne ikke bruke raspberry pi for databasen fordi den ikke lar meg installere nødvendige applikasjoner for å kunne linke pi-en sin database til spillet. ( men her er en liten tutorial på hva jeg skulle gjøre hvis PI-en min fungerte )

# Tutorial på hvordan man setter opp et system for high scores med en SQLite-database på en Raspberry Pi

# 🎮 Pygame High Score System med SQLite på Raspberry Pi

---

## 📋 **Funksjoner**

- **SQLite-database** for å lagre high scores med spillerens navn, poengsum og tidspunkt.  
- **Pygame-grensesnitt** som viser topplisten i spillet.  
- Enkle funksjoner for å legge til og hente high scores.  
- Kan kjøres på Raspberry Pi eller hvilken som helst datamaskin med Python og Pygame.  

---

## 🛠️ **Installasjon**

Følg disse stegene for å sette opp og kjøre prosjektet:

### **1. Installer nødvendige pakker**

Åpne terminalen og kjør følgende kommandoer:

```bash
sudo apt update
sudo apt install sqlite3 python3-pip
pip3 install pygame
