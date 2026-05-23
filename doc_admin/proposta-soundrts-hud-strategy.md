# SoundRTS — Proposta Strategica: Estensione HUD per Giocatori Normovedenti

**Tipo:** Proposta Strategica  
**Data:** 23 maggio 2026  
**Destinatario:** GitHub Copilot (Agent Mode)  
**Progetto:** fork `Nemex81/soundrts`  
**Autori:** Luca Profita + Perplexity AI Advisor

---

## Contesto e Obiettivo

SoundRTS è un gioco RTS open-source progettato storicamente per giocatori non vedenti. L'interfaccia primaria è audio: il gioco comunica tutto tramite sintesi vocale. Esiste già un layer visivo minimale (una griglia tattica 2D in Pygame) attivo in modalità fullscreen, ma è stato sempre trattato come secondario e non fornisce informazioni persistenti sul gameplay.

L'obiettivo di questa proposta è **estendere il client visivo esistente** aggiungendo un layer informativo che renda il gioco pienamente leggibile anche per un giocatore normovedente, senza alterare in alcun modo l'esperienza audio dei giocatori non vedenti. I due sistemi devono coesistere in modo trasparente.

---

## Principio Guida

> Non si crea un nuovo client. Si completa quello esistente.

Il client visivo è già presente e funzionante. L'audio continuerà a essere il canale primario. Il layer visivo diventa un **canale parallelo e complementare** che mostra in forma grafica le stesse informazioni che l'audio comunica vocalmente. Chi non guarda lo schermo non perde nulla. Chi guarda lo schermo guadagna leggibilità.

---

## Cosa Aggiungere

L'interfaccia estesa deve mostrare in modo visivo e persistente le informazioni già disponibili nel gioco ma attualmente accessibili solo tramite comandi vocali on-demand:

**Risorse del giocatore** — oro, legno, popolazione attuale e massima. Oggi queste informazioni vengono lette vocalmente solo quando il giocatore le richiede esplicitamente. Un giocatore normovedente si aspetta di vederle sempre visibili.

**Stato del gruppo selezionato** — quali unità sono attualmente sotto controllo, il loro ordine corrente, la loro salute. Oggi è accessibile solo tramite comando vocale.

**Feed degli eventi recenti** — una lista scorrevole degli ultimi eventi significativi del gameplay: combattimenti iniziati, edifici completati, settori sotto attacco, unità perse. Oggi questi eventi vengono comunicati vocalmente una sola volta e poi persi.

**Tempo di gioco e velocità** — informazioni di orientamento temporale, utili per gestire la strategia.

---

## Cosa NON Toccare

Questa proposta non richiede modifiche a:

- La logica di simulazione del gioco
- Il sistema di ordini
- Il networking multiplayer
- Il sistema audio e vocale
- Il pathfinding o il world state

L'estensione riguarda esclusivamente il **layer di presentazione visiva**, che nel codice è già separato dal resto.

---

## Approccio Suggerito

L'approccio preferito è **conservativo e incrementale**:

1. Analizzare prima come il client visivo attuale è strutturato e dove riceve i dati dal world state.
2. Identificare il punto più naturale dove agganciare i nuovi pannelli informativi senza interferire con il codice esistente.
3. Introdurre un meccanismo leggero per trasportare i dati dal world state ai nuovi pannelli, senza accoppiare la logica di gioco al layer visivo.
4. Costruire i monitor visivi come componenti autonomi e separati, che si aggiornano in risposta ai dati ricevuti.
5. Mantenere il tutto come **estensione opzionale**: se il layer visivo non è attivo, i monitor non vengono nemmeno istanziati.

---

## Stile Visivo di Riferimento

L'estetica deve rispecchiare la natura del progetto: **minimalismo tattico**. Riferimenti stilistici ideali sono DEFCON, Frozen Synapse, Duskers. Niente grafica elaborata, niente pannelli decorativi, niente icone animate. Solo dati chiari su sfondo scuro, leggibili a colpo d'occhio durante il gameplay.

L'obiettivo non è trasformare SoundRTS in un RTS visivo tradizionale. È rendere leggibile visivamente un gioco che funziona già benissimo senza immagini.

---

## Libertà Operativa per Copilot

Copilot ha piena libertà di:

- Rivedere questa proposta alla luce del codice reale trovato nel progetto
- Ottimizzare l'approccio in modo più coerente con la struttura esistente
- Proporre soluzioni tecniche diverse purché rispettino i vincoli strategici sopra
- Segnalare eventuali conflitti con la codebase attuale prima di procedere

La proposta descrive **cosa** si vuole ottenere e **come non** farlo. Il **come** farlo è responsabilità di Copilot dopo aver esaminato il codice in locale.

---

## Checklist di Validazione Attesa

Prima di considerare il lavoro completato, Copilot deve verificare che:

- [ ] Il layer audio funziona esattamente come prima, senza regressioni
- [ ] I monitor visivi si aggiornano correttamente ad ogni tick di gioco
- [ ] I nuovi componenti non introducono dipendenze circolari
- [ ] Il codice esistente di GridView non è stato modificato
- [ ] I nuovi file sono separati e identificabili chiaramente
- [ ] Il comportamento in assenza di display attivo è gestito senza errori
- [ ] Documentazione aggiornata e changelog compilato

---

*Proposta elaborata il 23 maggio 2026 — da sottoporre a Copilot in Agent Mode su VS Code*
