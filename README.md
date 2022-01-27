# Foerageren
Foerageren is dé website om de consumptie van jouw scoutinggroep bij te houden.

## Beschrijving
Iemand doet gezamenlijke inkopen, maar hoe houd je handig bij hoeveel iedereen daarvan heeft genomen? Lang niet iedereen zal hetzelfde hebben geconsumeerd, dus gelijk verdelen is oneerlijk. Daarvoor dient Foerageren. Alle leden hebben een account op de website en elke keer als ze iets pakken rekenen ze dat product af. De producten hebben een prijs die is aangegeven door de Manager, bij het afrekenen wordt deze prijs van het saldo van het lid afgetrokken. Leden hebben een saldo op de website, dat ze kunnen opwaarderen via Tikkies of overschrijvingen (of desnoods contante betalingen) aan de Manager, deze vult de bedragen in via het systeem zodat de saldo’s worden opgewaardeerd. 
Leden kunnen super makkelijk worden uitgenodigd door middel van een link. Ook kunnen leden in meerdere groepen zitten, waardoor alles netjes gescheden blijft. In deze video geeft Vincent een demonstratie van het gebruik van de website: https://youtu.be/hRCiBeVTeDM. 

## Inhoud
1. [Gebruikte technologie](#gebruikte-technologie)
2. [Handleiding](#handleiding)
    1. [Aanmelden](#aanmelden)
    2. [Groepen](#groepen)
    3. [Afrekenen](#afrekenen)
    4. [Producten toevoegen (voor managers)](#producten-toevoegen)
    5. [Saldo's bewerken en opwaarderen (voor managers)](#saldo's-bewerken-en-opwaarderen)
    6. [Vooraad bijhouden (voor managers)](#voorraad-bijhouden)
    7. [Gebruikers (voor managers)](#gebruikers)
3. [Credits](#credits)
4. [Licentie](#licentie)
5. [Bugs / toevoegingen](#bugs-toevoegingen)

## Gebruikte technologie
Foerageren is een web=application. De back-end is geprogrammeerd in Python met Django als web-framework. De front-end is gemaakt met Django-templates gecombineerd met Bootstrap v5.1 en custom CSS. Alle gebruikte packages staan in requirements.txt.

## Handleiding
### Aanmelden
Voor het gebruiken van Foergageren heb je een accout nodig, dit maak je aan door op Registeren te drukken: vul je gebruikersnaam en wachtwoord in. Vervolgens moet je een profiel aanmaken, hier vul je de naam in die anderen ook kunnen zien.

### Groepen
Voor het gebruik van Foerageren moet je in een groep zitten. Je kan zelf een groep aanmaken door een naam in te geven. Je kan ook aan een algemene groep deelnemen door op een link te klikken bovenin de pagina. Als je zelf een algemene groep wilt aanmaken moet je bij het aanmaken van je groep het hokje "Ik wil dat iedereen zich bij mijn groep kan aansluiten" aanvinken. Deelnemen aan een privé-groep kan via een uitnodigingslink die je krijgt van de manager van de groep. Je kan zo een link pas gebruiken zodra je een profiel hebt aangemaakt.
Je kan wisselen van groepen door bovenin op Wissel van groep te drukken. Ook kan je hier aan nieuwe algemene groepen deelnemen of zelf een nieuwe groep aanmaken door op Groep toevoegen te drukken.

### Afrekenen
Ga naar de Home-pagina (druk bovenin op je saldo). Selecteer het product dat je wilt verkopen en vink de mensen aan die het uit de kast hebben gepakt. Het aantal dat je invult is per persoon (dus als je 3 mensen aanvinkt en aantal 2 doet, gaat er 6 van de vooraad af en bij alle 3 de mensen 2 keer de prijs van dat product van hun saldo). Druk op afrekenen. 

### Producten toevoegen (voor managers)
Klik bovenin op het producten-tabje en voer de details in van je nieuwe product en druk op opslaan. Je kan bestaande producten bewerken door op de rode knop met hun naam erop te klikken. 

### Saldo's bewerken en opwaarderen (voor managers)
Klik bovenin op het opwaarderen-tabje. Zodra iemand jouw betaalverzoek betaald heeft kan je de gebruiker selecteren en het bedrag invoeren. Het saldo van die persoon wordt nu geupdated.

### Vooraad bijhouden (voor managers)
Zodra iets verkocht wordt, wordt ook de voorraad van dat product aangepast. Je kan onder het tabje vooraard een vooraad toevoegen / bewerken als je inkopen doet. Zo kan je altijd zien wat de voorraad is, zodat je precies weet wanneer je weer inkopen moet doen. 

### Gebruikers (voor managers)
Onder het tabje Gebruikers kan je zien wie er in jouw groep zitten, wat hun saldo is en welke functie zij bekleden. Ook kan je via hier naar de uitnodigingen-pagina, waar je een nieuwe link kan genereren die je kan delen met anderen, ook kan je oude links verwijderen zodat ze niet meer werken.

## Credits
Dank aan Arno Gregorian en Ricardo Tillemans voor het meewerken aan dit project.

## Licentie
Het is toegestaan om dit project te clonen en verder zelf te ontwikkelen. Gebruiken voor financiële doeleinden (zoals verkopen van accounts) is niet toegestaan.

## Bugs / toevoegingen
Maak gerust een pull-request aan om een bug aan te geven of een voorstel te doen voor een nieuwe functie