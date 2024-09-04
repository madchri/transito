# TransiTO
Applicazione per Android che consente di recuperare gli orari di transito dei veicoli della GTT (Gruppo Torinese Trasporti) ad una fermata specifica.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Funzionalità
**Notizie**:

Appena avviata, l'app accoglie l'utente con una pagina contenente tutti gli avvisi sulla mobilità recentemente pubblicati da GTT.

**Ricerca**:

Consente di salvare le fermate più utilizzate per un accesso più rapido, attribuendo loro un nome identificativo a piacere.

Nella parte superiore della pagina è ben evidenziata ed accessibile la barra di ricerca che consente di immettere il numero della fermata che si desidera per ottenere gli orari di transito.
Una volta eseguita, la ricerca mostra tutti i mezzi in arrivo alla fermata specificata, ognuno con il relativo orario.

**Impostazioni**:

Permette di consultare i crediti dell'applicazione, verificarne gli aggiornamenti e gestire alcune impostazioni.
- Tema scuro: consente di scegliere tra tema chiaro o scuro
- Cerca all'avvio: consente di far avviare l'app direttamente sulla pagina dei preferiti
- Orari semplici: consente di mostrare i minuti rimanenti all'arrivo del mezzo anzichè l'orario
- Elimina dati: consente di ripristinare tutte le impostazioni dell'app ai valori predefiniti
- GitHub: rimanda a questa pagina

## Creazione apk

Per creare l'apk a partire dal codice sorgente, utilzza questo comando dopo aver installato le librerie contenute nel file requirements.txt
```
flet build apk --product "TransiTO" --company "madchri" --org "com.madchri" --project "transito" --build-version "2.0.1" --no-android-splash --no-ios-splash --no-web-splash`
```

## Crediti
L'icona dell'app è stata ottenuta da icon-icons.com sotto licenza Creative Commons CC BY 4.0 Deed.

I dati sugli orari dei mezzi pubblici e gli avvisi di servizio presenti nell'app sono forniti da GTT e sono utilizzati solo a fine informativo.

La funzione per contattare l'api GraphQL di "Muoversi a Torino" (MATO) è stata da me sviluppata partendo dal lavoro svolto da @madbob con la sua "GTT Pirate API", disponibile su GitHub sotto licenza GPL-3.0.

L'applicazione è open source e non ha scopo di lucro.
