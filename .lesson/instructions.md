# Instruktioner: Projekt "Portfolio"

## Översikt

Skapa en personlig portföljwebbplats för att visa upp dina projekt och färdigheter. Webbplatsen bör innehålla åtminstone sidorna **Home**, **About**, **Projects** och **Contact**.

## To-Do

Följande uppgifter behöver genomföras:

- [ ] Skapa en personlig portföljwebbplats.
- [ ] Implementera ett CMS (Content Management System).
- [ ] Genomföra tester av webbplatsen.

### Sidor

För en effektiv och användarvänlig webbplats, bör varje sida följa en semantisk struktur bestående av `header`, `main` och `footer`. Denna struktur är inte bara viktig för användarupplevelsen utan också för SEO (Search Engine Optimization), vilket förbättrar webbplatsens synlighet i sökmotorer.

#### Home

- [ ] Skapa sidan med en `header`, `main` och `footer` struktur.
- [ ] Inkludera en navigationsmeny i headern med länkar till övriga sidor.
- [ ] Se till att innehållet i `main` ändras endast när användaren navigerar till andra sidor.

#### About

- [ ] Sidan bör vara en utvidgning av **Home**.
- [ ] Presentera dig själv med en kort biografi.
- [ ] Inkludera ett professionellt foto eller en illustrerande bild samt ditt CV.
- [ ] Använd denna sida för att dela din personliga historia, karriärambitioner och professionella mål.

#### Projects

- [ ] Sidan bör vara en utvidgning av **Home**.
- [ ] Visa dina projekt i listform eller som 'cards' med projektets namn och relevanta 'tags'.

#### Project Details

- [ ] Utvidga sidan `Projects` för att inkludera detaljerade beskrivningar av varje projekt, inklusive information om projektets natur och din roll.

#### Contact

- [ ] Sidan bör vara en utvidgning av **Home**.
- [ ] Implementera ett kontaktformulär för att möjliggöra för besökare att skicka meddelanden till dig.

#### Ytterligare sidor

- [ ] Implementera ytterligare sidor baserat på dina behov och preferenser.

### CMS (Content Management System)

Välj att skapa en egen CMS-sida eller använd en headless CMS-lösning.

#### Projects

- [ ] Implementera CRUD-operationer (Skapa, Läs, Uppdatera, Ta bort) för att hantera dina projekt.
  - [ ] Skapa: Lägg till nya projekt med detaljer som titel, beskrivning, använda teknologier, etc.
  - [ ] Läs: Organisera och visa alla dina projekt.
  - [ ] Uppdatera: Möjliggör ändringar i projektdetaljer.
  - [ ] Ta bort: Radera projekt som inte längre är aktuella eller relevanta.

#### Contact

- [ ] Integrera ett CMS för hantering av meddelanden från kontaktformuläret.
- [ ] Inkludera funktioner för att läsa och radera meddelanden i din CMS-dashboard.

### Tester

- [ ] Testa din webbplats manuellt på olika webbläsare och enheter för att säkerställa kompatibilitet och användarvänlighet.

## Cheatsheets

- [Flask](https://www.codecademy.com/learn/introduction-to-flask/modules/introduction-to-flask/cheatsheet)
- [Jinja2 Templates and Forms](https://www.codecademy.com/learn/introduction-to-flask/modules/flask-templates-and-forms/cheatsheet)
- [UI Elements](https://www.visily.ai/blog/ui-elements/)
- [Git](https://www.freecodecamp.org/news/git-cheat-sheet/)

## HTTP Metoder

Använd enbart **GET** och **POST** metoder för att utföra alla **CRUD**-operationer.

## Starta din server

Det finns två enkla sätt att starta din server:

1. **Klicka på knappen:**
   ![Run](assets/run.png)
2. **Kör följande kommando i Shell:**

```shell
python app.py
```
