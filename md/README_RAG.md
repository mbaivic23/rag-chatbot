---
title: "README za RAG bazu znanja"
domain: "Chatbot za kućnu fermentaciju"
language: "hr"
version: "1.0"
source_type: "upute za korištenje podataka"
tags: ["RAG", "baza znanja", "kućna fermentacija", "chatbot"]
---

# README za RAG bazu znanja

Ova mapa sadrži tekstualne dokumente u Markdown formatu koji su pripremljeni kao početna baza znanja za chatbot za kućnu fermentaciju. Dokumenti su namijenjeni korištenju u RAG arhitekturi, odnosno u sustavu u kojem chatbot prije generiranja odgovora dohvaća relevantne dijelove teksta iz baze znanja i zatim na temelju njih oblikuje odgovor korisniku.

Sadržaj je organiziran tako da svaki dokument pokriva jednu logičku cjelinu domene. Takva podjela olakšava indeksiranje, pretraživanje, izradu embeddinga i kasnije održavanje baze znanja. Dokumenti su pisani jednostavnim hrvatskim jezikom jer je cilj chatbota pomoći početnicima koji nemaju tehničko, mikrobiološko ili prehrambeno-tehnološko predznanje.

Za početnu verziju RAG sustava preporučuje se učitati sve Markdown datoteke iz ove mape. Prilikom obrade teksta korisno je čuvati metapodatke iz YAML zaglavlja, osobito naslov, oznake i kategoriju dokumenta. Ti metapodaci mogu pomoći sustavu da preciznije pronađe odgovarajući izvor za korisničko pitanje. Primjerice, ako korisnik pita o kombuchi, sustav bi trebao dati prednost dokumentima koji u oznakama sadrže pojam "kombucha" ili "fermentacija čaja".

Kod izrade chunkova preporučuje se da jedan chunk obuhvaća jednu do dvije povezane sekcije. Prekratki chunkovi mogu izgubiti kontekst, dok predugi chunkovi mogu otežati precizno dohvaćanje. Dobar početni raspon za ovu domenu je približno 500 do 900 riječi po chunku, uz preklapanje od jedne kraće cjeline ako se koriste dulji dokumenti.

Chatbot mora odgovarati samo unutar domene kućne fermentacije. Ako korisnik postavi pitanje koje nije vezano uz fermentaciju hrane i pića u kućnim uvjetima, sustav treba ljubazno odbiti odgovor i objasniti da je namijenjen temama poput kiselog kupusa, kimchija, kefira, kombuche i kiselog tijesta. Ako korisnik traži medicinski savjet, dijagnozu, liječenje, savjet za alergije ili postupanje kod mogućeg trovanja hranom, chatbot treba jasno navesti da ne zamjenjuje stručnjaka i da se korisnik u takvim slučajevima treba obratiti liječniku ili drugoj nadležnoj stručnoj osobi.

Ova baza znanja nije zamišljena kao konačan skup izvora, nego kao početna struktura. U kasnijim fazama projekta preporučuje se dodati provjerene izvore, primjerice stručne priručnike, edukativne članke, smjernice o sigurnosti hrane, studentske materijale i vlastite tekstove izrađene za potrebe projekta. Svaki novi dokument treba biti napisan jasno, strukturirano i s naglaskom na sigurnost korisnika.
