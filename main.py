from requests import get
from feedparser import parse
from bs4 import BeautifulSoup
from datetime import datetime
from mato import passaggi, orari
from flet import app, colors, AlertDialog, AppBar, Badge, Card, Column, Container, Divider, FilledButton, FilledTonalButton, FontWeight, Icon, icons, ListTile, MainAxisAlignment, NavigationBar, NavigationDestination, padding, ProgressBar, Row, SnackBar, Switch, Text, TextButton, TextField, TextOverflow, ThemeMode, IconButton

def main(pagina):

    VERSIONE = "1.5.0"
    pagina.ricerca = False
    pagina.scroll = "hidden"
    pagina.aggiornata = True
    pagina.ultima_pagina = 0
    pagina.theme_mode = ThemeMode.DARK
    pagina.horizontal_alignment = "center"

    # Cambia le pagine tramite NavBar
    def cambia_pagina(e):
        if e.control.selected_index == 0:
            carica_avvisi()
        elif e.control.selected_index == 1:
            if pagina.ricerca == False:
                if pagina.ultima_pagina == 0:
                    pagina.navbar.selected_index = 0
                else:
                    pagina.navbar.selected_index = 2
                pagina.update()
        else:
            carica_impostazioni()
    
    # Torna alla pagina precedente
    def torna_indietro(e):
        if pagina.ultima_pagina == 0:
            pagina.navbar.selected_index = 0
            carica_avvisi()
        else:
            pagina.navbar.selected_index = 2
            carica_impostazioni()

    # Verifica il tema dell'app
    def verifica_tema():
        tema = pagina.client_storage.get("tema")
        if tema == True:
            pass
        elif tema == False:
            pagina.swc_tema.value = False
            pagina.theme_mode = ThemeMode.LIGHT
        else:
            pagina.client_storage.set("tema", True)

    # Cambia il tema dell'app
    def cambia_tema(e):
        if pagina.theme_mode == ThemeMode.DARK:
            pagina.theme_mode = ThemeMode.LIGHT
            pagina.client_storage.set("tema", False)
        else:
            pagina.theme_mode = ThemeMode.DARK
            pagina.client_storage.set("tema", True)
        pagina.update()
    
    # Verifica Cerca all'avvio
    def verifica_avvio():
        avvio = pagina.client_storage.get("avvio")
        if avvio == False:
            pass
        elif avvio == True:
            pagina.swc_avvio.value = True
            pagina.txt_ricerca.autofocus = True
        else:
            pagina.client_storage.set("avvio", False)

    # Modifica Cerca all'avvio
    def cambia_avvio(e):
        if pagina.swc_avvio.value == True:
            pagina.client_storage.set("avvio", True)
        else:
            pagina.client_storage.set("avvio", False)
    
    # Chiude i dialoghi
    def chiudi_dialogo(e):
        pagina.alertdg.open = False
        pagina.update()
    
    # Apre il link di GitHub
    def apri_github(e):
        URL_GITHUB = "https://github.com/madchri/to-bus/"
        pagina.launch_url(URL_GITHUB)
    
    # Avvia download aggiornamento
    def avvia_download(e):
        URL_DOWNLOAD = "https://github.com/madchri/to-bus/releases/latest/download/to-bus.apk"
        pagina.launch_url(URL_DOWNLOAD)
    
    # Mostra la pagina Impostazioni
    def carica_impostazioni():
        pagina.ricerca = False
        pagina.ultima_pagina = 2
        firma = Container(content = Text("2024 • @madchri", size = 12), padding = 14)
        layout_superiore2 = AppBar(title = Column(controls = [Row(controls = [IconButton(icon = icons.SETTINGS_OUTLINED, icon_size = 30), pagina.txt_ricerca, IconButton(icon = icons.SEARCH, icon_size = 30, tooltip = "Cerca", on_click = stampa_passaggi)])]), center_title = True, toolbar_height = 85, elevation = 0, bgcolor=colors.SURFACE)
        crd_informazioni = Card(content = Container(content = Column([ListTile(title = Text("Informazioni", size = 15)), ListTile(leading = Icon(icons.INFO_OUTLINE, color = colors.ON_BACKGROUND),title = Text("Crediti", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Dettagli sull'app"), trailing = FilledTonalButton(text = "GitHub", icon = icons.OPEN_IN_NEW, width = 118, on_click = apri_github))], spacing = 0),padding=padding.symmetric(vertical = 10, horizontal = 4)))
        crd_generali = Card(content = Container(content = Column([ListTile(title = Text("Generali", size = 15)), ListTile(leading = Icon(icons.DARK_MODE_OUTLINED, color = colors.ON_BACKGROUND),title = Text("Tema scuro", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Affatica meno la vista"), trailing = pagina.swc_tema), ListTile(leading = Icon(icons.SEARCH, color = colors.ON_BACKGROUND),title = Text("Cerca all'avvio", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Apri subito la ricerca"), trailing = pagina.swc_avvio)], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)))
        pagina.clean()
        if pagina.aggiornata == False:
            pagina.add(layout_superiore2, pagina.crd_aggiorna, crd_generali, crd_informazioni, firma, pagina.navbar)
        else:
            pagina.add(layout_superiore2, crd_generali, pagina.crd_aggiorna, crd_informazioni, firma, pagina.navbar)

    # Controlla gli aggiornamenti
    def verifica_aggiornamenti():
        URL_AGGIORNA = "https://api.github.com/repos/madchri/to-bus/releases/latest"
        try:
            risposta = get(URL_AGGIORNA).json()
            if risposta["name"] > VERSIONE:
                pagina.aggiornata = False
                pagina.alertdg = AlertDialog(title = Text("Aggiornamento", text_align = "center", weight = FontWeight.W_600), icon = Icon(icons.UPDATE), content = Text(risposta["body"]), modal = True, open = True, actions = [TextButton(text = "Non ora", icon = icons.CLOSE, on_click = chiudi_dialogo), TextButton(text = "Scarica", icon = icons.DOWNLOAD,on_click = avvia_download)], actions_alignment = MainAxisAlignment.SPACE_BETWEEN)
                pagina.navbar = NavigationBar(destinations = [NavigationDestination(icon = icons.HOME_OUTLINED, selected_icon = icons.HOME, label = "Avvisi"), NavigationDestination(icon = icons.SEARCH_OUTLINED, selected_icon = icons.SEARCH, label = "Ricerca"), NavigationDestination(icon_content = Badge(content = Icon(icons.SETTINGS_OUTLINED), small_size=10), selected_icon_content = Badge(content = Icon(icons.SETTINGS), small_size=10), label = "Impostaz.")], on_change = cambia_pagina)
                pagina.crd_aggiorna = Card(content = Container(content = Column([ListTile(title = Text("Aggiornamenti", size = 15)), ListTile(leading = Icon(icons.UPDATE, color = colors.ON_BACKGROUND), title = Text("Aggiorna l'app", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Versione " + risposta["name"]), trailing = FilledButton(text = "Scarica", icon = icons.DOWNLOAD, width = 122, on_click = avvia_download))], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)), color = colors.SECONDARY_CONTAINER)
                pagina.add(pagina.navbar, pagina.alertdg)
        except Exception:
            pass

    # Carica il feed avvisi
    def carica_avvisi():
        pagina.ricerca = False
        pagina.ultima_pagina = 0
        pgb_caricamento = ProgressBar(bgcolor = colors.TRANSPARENT, visible = True)
        layout_superiore0 = AppBar(title = Column(controls = [Row(controls = [IconButton(icon = icons.HOME_OUTLINED, icon_size = 30), pagina.txt_ricerca, IconButton(icon = icons.SEARCH, icon_size = 30, tooltip = "Cerca", on_click = stampa_passaggi)])]), center_title = True, toolbar_height = 85, elevation = 0, bgcolor = colors.SURFACE)
        pagina.clean()
        pagina.add(layout_superiore0, pgb_caricamento, pagina.navbar)
        try:
            URL_FEED = "https://www.gtt.to.it/cms/avvisi-e-informazioni-di-servizio?format=feed"
            avvisi = parse(URL_FEED)["entries"]
            if pagina.navbar.selected_index == 0:
                pgb_caricamento.visible = False
                for avviso in avvisi:
                    stringhe = BeautifulSoup(avviso["summary"], features = "html.parser").findAll(string = True)
                    contenuto = "\n" + "".join(stringhe)
                    contenuto = contenuto.replace("Leggi tutto...", "")
                    if contenuto.endswith("\n"):
                        contenuto = contenuto.rsplit("\n", 1)[0]
                    card = Card(content = Container(content = Column([ListTile(title = Text(avviso["title"], weight = FontWeight.W_600), subtitle = Text(contenuto))], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4), border_radius = 10))
                    pagina.add(card)
        except Exception:
            pass

    # Visualizza i dati formattati a video
    def stampa_passaggi(e):
        ora = datetime.now()
        dati = passaggi(pagina.txt_ricerca.value, ora)
        if len(dati) > 0:
            pagina.ricerca = True
            pagina.navbar.selected_index = 1
            layout_superiore1 = AppBar(title = Column(controls = [Row(controls = [IconButton(icon = icons.ARROW_BACK, tooltip = "Indietro", icon_size = 30, on_click = torna_indietro), pagina.txt_ricerca, IconButton(icon = icons.REFRESH, icon_size = 30, tooltip = "Aggiorna", on_click = stampa_passaggi)])]), center_title = True, toolbar_height = 85, elevation = 0, bgcolor = colors.SURFACE)
            pagina.clean()
            pagina.add(layout_superiore1, pagina.navbar)
            for linea in dati:
                timestamps = orari(linea["realtimeArrival"], ora)
                if linea["realtime"] == True:
                    stato = "IN TEMPO REALE"
                    minuti = Text(timestamps[0], size = 25, color = colors.GREEN)
                else:
                    stato = "PROGRAMMATO"
                    minuti = Text(timestamps[0], size = 25, color = colors.ON_BACKGROUND)
                if linea["trip"]["pattern"]["route"]["mode"] == "TRAM":
                    icona = Icon(icons.TRAM_SHARP, size = 26, color = colors.ON_BACKGROUND)
                else:
                    icona = Icon(icons.DIRECTIONS_BUS, size = 26, color = colors.ON_BACKGROUND)
                if linea["trip"]["wheelchairAccessible"] == "POSSIBLE":
                    wheel = Icon(icons.ACCESSIBLE, color = colors.ON_BACKGROUND)
                else:
                    wheel = Icon(icons.NOT_ACCESSIBLE, color = colors.ON_BACKGROUND)
                crd_mezzo = Card(content = Container(content = Column([ListTile(leading = icona, title = Text(linea["trip"]["pattern"]["route"]["shortName"], size = 25, weight = FontWeight.W_500, color = colors.ON_BACKGROUND), trailing = minuti), Divider(thickness = 0), ListTile(leading = Icon(icons.ACCESS_TIME, color = colors.ON_BACKGROUND), title = Text(stato, size = 13, color = colors.ON_BACKGROUND, weight = FontWeight.W_500), trailing = Text(timestamps[1], size = 13, color = colors.ON_BACKGROUND, weight = FontWeight.W_500)), ListTile(leading = Icon(icons.DIRECTIONS_OUTLINED, color = colors.ON_BACKGROUND), title = Text(linea["trip"]["tripHeadsign"], size = 13, color = colors.ON_BACKGROUND, no_wrap = True, overflow = TextOverflow.FADE, weight = FontWeight.W_500), trailing = wheel)], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4), border_radius = 10))
                pagina.add(crd_mezzo)
            ora_attuale = ora.strftime("%H:%M")
            timestamp = Container(content = Text("dati aggiornati alle " + ora_attuale, size = 12), padding = 14)
            pagina.add(timestamp)
        else:
            snb_noinfo = SnackBar(content = Text("Nessuna informazione disponibile"), open = True)
            pagina.add(snb_noinfo)

    # Elementi layout globali
    pagina.alertdg = AlertDialog()
    pagina.swc_tema = Switch(on_change = cambia_tema, value = True)
    pagina.swc_avvio = Switch(on_change = cambia_avvio, value = False)
    pagina.txt_ricerca = TextField(filled = True, hint_text = "Cerca fermata", text_align = "center", text_vertical_align = 1.0, keyboard_type = "number", border_radius = 100, height = 56.0, expand = True, autofocus = False, on_submit = stampa_passaggi)
    pagina.navbar = NavigationBar(destinations = [NavigationDestination(icon = icons.HOME_OUTLINED, selected_icon = icons.HOME, label = "Avvisi"), NavigationDestination(icon = icons.SEARCH_OUTLINED, selected_icon = icons.SEARCH, label = "Ricerca"), NavigationDestination(icon = icons.SETTINGS_OUTLINED, selected_icon = icons.SETTINGS, label = "Impostaz.")], on_change = cambia_pagina)
    pagina.crd_aggiorna = Card(content = Container(content = Column([ListTile(title = Text("Aggiornamenti", size = 15)), ListTile(leading = Icon(icons.UPDATE, color = colors.ON_BACKGROUND), title = Text("App aggiornata", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Versione " + VERSIONE), trailing = IconButton(icon = icons.CHECK, icon_size = 30, bgcolor = colors.SECONDARY_CONTAINER, icon_color = colors.ON_BACKGROUND))], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)))

    # Caricamento iniziale
    verifica_tema()
    verifica_avvio()
    carica_avvisi()
    pagina.txt_ricerca.autofocus = False
    verifica_aggiornamenti()

app(main)
