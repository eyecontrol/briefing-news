# Il Briefing Mattiniero

Ogni mattina una pagina in stile quotidiano con le notizie che contano, raccolte solo da testate storiche italiane, serbe e internazionali. Sezioni: Politica, Guerre, Catastrofi, Economia e finanza, Scienza, Medicina, Tecnologia. Sport, spettacolo, gossip e lifestyle sono esclusi. In alto si sceglie l'edizione (**Mondo**, **Italia** o **Serbia**) e la lingua delle notizie (italiano, inglese o serbo).

## Come funziona

- Ogni giorno alle 04:00 UTC (06:00 ora legale, 05:00 ora solare) GitHub Actions esegue `python -m briefing.build`.
- Lo script legge i feed RSS elencati in `briefing/sources.py`, scarta le notizie vecchie, quelle di sport e spettacolo e la cronaca che non rientra in nessuna sezione.
- La stessa notizia ripresa da più testate viene unita; quelle riprese da più giornali salgono in apertura.
- La pagina generata (`site/index.html`) viene pubblicata su GitHub Pages.
- Ogni mattina il workflow si riattiva da solo, così GitHub non lo sospende dopo 60 giorni senza modifiche.

Non servono librerie esterne: solo Python 3.11 o successivo.

## Prima attivazione

1. In **Settings → Pages**, alla voce *Build and deployment*, scegli **Source: GitHub Actions**.
2. Su un repository privato GitHub Pages richiede un piano a pagamento (GitHub Pro). In alternativa rendi pubblico il repository: il codice non contiene dati personali.
3. Per avere subito il primo numero: **Actions → Briefing mattiniero → Run workflow**.

L'indirizzo della pagina compare in Settings → Pages e nel riepilogo di ogni esecuzione.

## Cambiare fonti o regole

- Testate e feed: `briefing/sources.py`
- Parole chiave per sezioni, esclusioni e notizie italiane: `briefing/classify.py`
- Grafica: `template/index.html`

Ogni esecuzione stampa lo stato di ogni feed (passaggio *Stato dei feed*), utile per accorgersi se un giornale cambia indirizzo.

## Prova in locale

```
python -m unittest discover -s tests -t .
python -m briefing.build --out site
```
