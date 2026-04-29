---
title: "Opis izvora i vrste podataka za RAG"
domain: "Chatbot za kućnu fermentaciju"
language: "hr"
version: "1.0"
source_type: "opis RAG podataka"
tags: ["RAG", "izvori podataka", "vektorska baza", "baza znanja", "projekt"]
---

# Opis izvora i vrste podataka za RAG

Za rad chatbota za kućnu fermentaciju koristit će se baza znanja pripremljena u obliku tekstualnih dokumenata. Ti dokumenti predstavljaju temelj za RAG pristup, odnosno za arhitekturu u kojoj chatbot ne odgovara samo na temelju općeg znanja jezičnog modela, nego prije odgovaranja dohvaća relevantne dijelove provjerene baze znanja. Takav pristup je posebno važan u ovoj domeni jer se odgovori često odnose na sigurnost hrane, prepoznavanje kvarenja i praktične korake koje korisnik provodi u stvarnom kućnom okruženju.

Izvori podataka u početnoj fazi uključuju projektne dokumente koji definiraju domenu chatbota, funkcionalne i nefunkcionalne zahtjeve, očekivane slučajeve korištenja i sigurnosna ograničenja sustava. Na temelju tih dokumenata oblikuju se tekstovi koji opisuju četiri glavne kategorije fermentacije: fermentaciju povrća, mliječnu fermentaciju, fermentaciju čaja i fermentaciju kruha. Svaka kategorija treba imati vlastiti sadržaj kako bi RAG sustav mogao precizno dohvatiti informacije o temi koju korisnik spominje u upitu.

Osim projektnih dokumenata, u bazu znanja mogu se uključiti edukativni tekstovi o osnovnim principima fermentacije, vodiči po koracima, popisi potrebne opreme, opisi normalnih znakova fermentacije i opisi znakova mogućeg kvarenja. Posebnu skupinu podataka čine sigurnosne smjernice. One trebaju biti napisane jasno i oprezno jer chatbot mora znati kada korisniku preporučiti nastavak fermentacije, a kada odbacivanje proizvoda. Sigurnosni tekstovi trebaju sadržavati primjere poput pojave obojene plijesni, neugodnog trulog mirisa, promjene boje ili drugih znakova koji mogu upućivati na kontaminaciju.

Podaci za RAG trebaju biti pripremljeni u Markdown formatu jer je taj format jednostavan za čitanje, uređivanje i automatsku obradu. Markdown dokumenti mogu sadržavati naslove, podnaslove, odlomke i metapodatke. Naslovi i podnaslovi pomažu sustavu pri segmentaciji teksta, a metapodaci omogućuju dodatno filtriranje sadržaja. Primjerice, dokument koji se odnosi na kombuchu može sadržavati oznake "kombucha", "fermentacija čaja" i "SCOBY", čime se povećava vjerojatnost da će biti dohvaćen za korisnički upit o kombuchi.

Prije spremanja u vektorsku bazu, dokumente je potrebno podijeliti na manje dijelove. Ti dijelovi trebaju biti dovoljno veliki da zadrže smisao, ali dovoljno mali da dohvat bude precizan. Ako je chunk prekratak, model može izgubiti kontekst. Ako je predug, sustav može dohvatiti previše nepotrebnih informacija. Za ovaj projekt prikladno je da jedan chunk obuhvati jednu tematsku cjelinu, primjerice objašnjenje normalnih znakova fermentacije kod kefira ili sigurnosne preporuke za plijesan na kombuchi.

Baza znanja treba biti odvojena od samog jezičnog modela. To znači da se sadržaj može ažurirati bez ponovnog treniranja modela. Ako se kasnije doda nova kategorija, primjerice fermentacija octa ili fermentacija sojinih proizvoda, potrebno je dodati nove dokumente u bazu znanja, izraditi njihove embeddinge i uključiti ih u pretraživanje. Takav pristup omogućuje proširivost sustava i izravno podržava zahtjev da se nove kategorije mogu dodavati bez cjelovitog redizajna arhitekture.

Kod odgovaranja korisniku chatbot treba koristiti dohvaćene podatke kao glavni izvor. Ako korisnik pita o sigurnosti proizvoda, sustav treba dohvatiti dokumente koji se odnose na sigurnost hrane i znakove kvarenja. Ako korisnik pita za vodič, sustav treba dohvatiti vodiče po koracima. Ako korisnik pita što mu je potrebno od opreme, sustav treba dohvatiti dokument o opremi i higijeni. Time se povećava relevantnost odgovora i smanjuje rizik da chatbot generira neprovjerene ili nepovezane informacije.

Važno je da RAG baza ne sadrži samo recepte, nego i pravila ponašanja sustava. Chatbot mora znati kada odbiti pitanje izvan domene, kada postaviti dodatno pitanje i kada dati sigurnosno upozorenje. Zbog toga u bazu treba uključiti i dokumente koji definiraju ograničenja domene, način komunikacije s početnicima i postupanje u rizičnim situacijama. Ti dokumenti pomažu da odgovori budu dosljedni, sigurni i usklađeni sa svrhom projekta.
