# Kurssisovellus

Sovelluksessa opettajat voivat luoda kursseja ja tehtäviä kurseille. Opiskelijat voivat liittyä kursseille, tehdä tehtäviä ja nähdä tekemänsä tehtävät. Opettajat näkevät kurssinsa oppilaat ja heidän läpäisemänsä tehtävät. Opettajat pystyvät luomaan tehtäviä, joissa on kirjallinen kysymys ja erillinen 
vastuskenttä ja lisäksi he voivat tehdä monivalintakysymyksiä.

Kun uusi kurssi luodaan, se on aluksi tilassa, jossa kursille voi lisätä tehtäviä. Tällöin kurssi ei ole näkyvissä kenellekään muulle kuin kurssin opettajalle. Tämän jälkeen opettaja voi aloittaa kurssin, jolloin kurssi tulee näkyviin muille ja opiskelijat voivat liittyä kurssille ja alkaa tehdä tehtäviä. Tässä vaiheessa opettaja ei voi enää lisätä tai poistaa tehtäviä. Lopulta opettaja voi sulkea kurssin, jonka jälkeen kurssi ei ole enää näkyvissä muille kuin sille jo liittyneille eikä tehtävien teko ole enää mahdollista. Kurssihaussa listataan kerralla 20 kurssia akkosjärjestyksessä ja lisäksi kursseja voi hakea tarkan nimihaun perusteella.

Sovelluksessa on seuraavia ominaisuuksia.

* Käyttäjä voi luoda uuden tunnuksen opiskelijana tai opettajana.
* Käyttäjä voi kirjautua sisään ja ulos.
* Käyttäjät voivat nähdä käynnissä olevat kurssit.
* Käyttäjät voivat nähdä omat kurssinsa.
* Opiskelija voi liittyä kurssille ja tehdä tehtäviä.
* Opiskelija voi nähdä mitkä tehtävät hän on tehnyt.
* Opettaja voi luoda kurssin
* Opettaja voi tehdä tehtäviä.
* Opiskelija pystyy näkemään ratkaisemansa tehtävät ja lähettämänsä vastaukset.
* Opettaja voi tehdä monivalintakysymyksiä.
* Opettaja voi nähdä kurssinsa opiskelijat ja heidän tilastonsa.
* Tehtäviä voi poistaa ennen kurssin aloittamista
* Kursseja voi hakea nimellä

## Sovelluksen testaaminen

Sovellusta voi testata paikallisesti. Kloonaa tämä repositorio koneellesi ja siirry sen juurikansioon. Aktivoi virtuaaliympäristö komennoilla 

    $ python3 -m venv venv  
    $ source venv/bin/activate
    
Asenna riippuvuudet komennolla

    (venv) $ pip install -r requirements.txt

Luo Postgresiin uusi tietokanta komennoilla

    $ psql  
    user=# CREATE DATABASE <tietokannan_nimi>;

Määritä sitten tietokannan skeema komennolla

    $ psql -d <tietokannan_nimi> < schema.sql

Luo sovelluksen juurikansioo vielä .env -tiedosto ja määritä siellä salainen avaimesi ja tietokannan osoite

    DATABASE_URL=postgresql+psycopg2:///<tietokannan_nimi>  
    SECRET_KEY=<salainen avaimesi>

Nyt olet valmis testamaan sovellusta komennolla 

    $ flask run


