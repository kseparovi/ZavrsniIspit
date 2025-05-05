# Django Web Scraping Project

## Opis Projekta
Ovaj projekt je Django web aplikacija koja prikuplja, normalizira i prikazuje recenzije mobitela s različitih web stranica koristeći web scraping. Recenzije se spremaju u bazu podataka, a korisnici ih mogu pregledati putem web sučelja.

## Tehnologije
- **Django** - Backend framework
- **SQLite** - Baza podataka
- **BeautifulSoup** - Web scraping
- **Requests** - Za dohvaćanje HTML sadržaja web stranica

## Kako Postaviti Projekt
### 1. Kloniranje repozitorija
```sh
 git clone https://github.com/korisnickoime/ZavrsniIspit.git
 cd ZavrsniIspit
```
### 2. Kreiranje i aktivacija virtualnog okruženja
```sh
 python -m venv env
 source env/bin/activate  # Za Windows: env\Scripts\activate
```
### 3. Instalacija paketa
```sh
 pip install -r requirements.txt
```
### 4. Pokretanje migracija baze podataka
```sh
 python manage.py migrate
```
### 5. Pokretanje aplikacije
```sh
 python manage.py runserver
```
Aplikacija će biti dostupna na `http://127.0.0.1:8000/`

## Web Scraping
Web scraping se izvodi pomoću **BeautifulSoup** biblioteke. Skripte za scraping dohvaćaju recenzije s web stranica poput:
- [GSMArena](https://www.gsmarena.com/)
- [PhoneArena](https://www.phonearena.com/)
- 
Svaka skripta izdvaja:
- Tekst recenzije
- Numeričku ocjenu
- Korisničko ime (ako je dostupno)

## Normalizacija Recenzija
Budući da različite web stranice koriste različite ocjene (npr. 1-5, 1-10, thumbs up/down), ocjene se normaliziraju kako bi bile usporedive.

## Prikaz u Django Aplikaciji
Prikupljene recenzije se spremaju u bazu i prikazuju na web stranici, omogućujući korisnicima filtriranje i pregled različitih ocjena i komentara.

## Kontakt
Za više informacija, kontaktirajte autora projekta putem e-maila: **kseparovi@student.unizd.hr**.



## NLP

Većina NLP alata koristi ove klasifikacije:
✅ Binarna klasifikacija

    Positive

    Negative

Primjer: TextBlob koristi polarity skor od -1 do 1, gdje je sve ispod 0 negativno, a iznad pozitivno.


✅ Ternarna klasifikacija

    Positive

    Neutral

    Negative

Primjer: VADER (iz NLTK) koristi compound vrijednost:

    >= 0.05: pozitivno

    <= -0.05: negativno

    između: neutralno

✅ Ordinalna klasifikacija (1–5 zvjezdica)

Koriste je modeli kao nlptown/bert-base-multilingual-uncased-sentiment (na HuggingFace):

    1 star = vrlo negativno

    3 stars = neutralno

    5 stars = vrlo pozitivno



## Crontab skripta
crontab -e
0 12 * * * /home/pakel/PycharmProjects/ZavrsniIspit/.venv/bin/python /home/pakel/Desktop/ZavrsniIspit/manage.py scrape_reviews >> /home/pakel/Desktop/ZavrsniIspit/logs/scrape.log 2>&1

Ova linija će pokrenuti Django skriptu `scrape_reviews` svaki dan u 12:00 sati. Rezultati će biti spremljeni u `scrape.log` datoteku, a svi errori će biti preusmjereni u istu datoteku.