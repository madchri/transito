from requests import get
from feedparser import parse
from bs4 import BeautifulSoup
from datetime import datetime
from mato import passaggi_mato
from gtfs import ottieni_gtfs, avvisi_gtfs
from flet import app, colors, icons, padding, AlertDialog, AppBar, Badge, BottomSheet, Card, Chip, Column, Container, CrossAxisAlignment, Divider, ExpansionTile, FilledButton, FilledTonalButton, FontWeight, Icon, IconButton, ListTile, MainAxisAlignment, MainAxisAlignment, NavigationBar, NavigationDestination, NavigationBarLabelBehavior, PagePlatform, ProgressBar, RoundedRectangleBorder, Row, ScrollMode, SnackBar, Switch, Text, TextButton, TextField, TextOverflow, ThemeMode, TextCapitalization, VerticalAlignment

def main(pagina):

    VERSIONE = "1.9.0"
    pagina.avvisi = []
    pagina.ricerca = False
    pagina.aggiornata = True
    pagina.ultima_pagina = 0
    pagina.title = "TransiTO"
    pagina.auto_scroll = False
    pagina.feed_caricato = False
    pagina.filtro = "Torino e cintura"

    pagina.scroll = ScrollMode.HIDDEN
    pagina.theme_mode = ThemeMode.DARK
    pagina.platform = PagePlatform.ANDROID
    pagina.vertical_alignment = VerticalAlignment.CENTER
    pagina.horizontal_alignment = CrossAxisAlignment.CENTER

    # Pagina dei Preferiti
    def carica_preferiti():
        pagina.ultima_pagina = 1
        pagina.navbar.selected_index = 1
        layout_superiore1 = AppBar(title=Column(controls=[Row(controls=[IconButton(icon=icons.STAR_OUTLINE, icon_size=30),pagina.txt_ricerca,IconButton(icon=icons.SEARCH, icon_size=30, tooltip="Cerca", on_click=stampa_passaggi)])]),center_title=True,toolbar_height=85,elevation=0,bgcolor=colors.SURFACE)
        pagina.clean()
        pagina.add(layout_superiore1, pagina.navbar)

        preferiti = pagina.client_storage.get("preferiti")
        if preferiti:
            for preferito in preferiti:
                nome_preferito = preferito.get("nome")
                numero_preferito = preferito.get("numero")
                pref = Card(content = Container(padding = padding.symmetric(vertical = 10, horizontal = 4),content = Column([ListTile(leading = Icon(icons.PUSH_PIN_OUTLINED, color = colors.ON_BACKGROUND, size=22),title = Text(nome_preferito, weight = FontWeight.W_500, color = colors.ON_BACKGROUND, size = 22), trailing = Text(numero_preferito, weight = FontWeight.W_500, size = 22), on_click=cerca_preferito, on_long_press=elimina_preferito)])), color=colors.SECONDARY_CONTAINER)
                pagina.add(pref)
            pagina.add(Divider(thickness=0))
        recenti = pagina.client_storage.get("recenti")
        if recenti:
            for fermata in recenti:
                rec = Card(content = Container(padding = padding.symmetric(vertical = 10, horizontal = 4),content = Column([ListTile(leading = Icon(icons.HISTORY, color = colors.ON_BACKGROUND, size=22),title = Text("Fermata", weight = FontWeight.W_500, color = colors.ON_BACKGROUND, size = 22), trailing = Text(fermata, weight = FontWeight.W_500, size = 22), on_click=cerca_preferito)])))
                pagina.add(rec)
            pagina.add(Divider(thickness=0, color=colors.TRANSPARENT), FilledTonalButton(icon = icons.ADD, text = "Aggiungi", on_click = aggiungi_preferito))
        else:
            pagina.add(Text("", size=130), Text("Nessun preferito", weight=FontWeight.W_500, size=20), Text("", size=0), FilledTonalButton(icon = icons.ADD, text = "Aggiungi", on_click = aggiungi_preferito))

    # Ricerca preferito
    def cerca_preferito(e):
        pagina.txt_ricerca.value = e.control.trailing.value
        stampa_passaggi(e)
    
    def elimina_preferito(e):
        num = e.control.trailing.value
        preferiti = pagina.client_storage.get("preferiti")
        for record in preferiti:
            if record["numero"] == num:
                preferiti.remove(record)
                pagina.client_storage.set("preferiti", preferiti)
                carica_preferiti()
                pagina.add(SnackBar(content=Text("Preferito eliminato"), open=True))
                break

    # Aggiunta preferito
    def aggiungi_preferito(e):
        nome = TextField(icon=icons.TEXT_FIELDS,hint_text="Nome (a piacere)",border_radius=15,filled=True,autofocus=True,capitalization = TextCapitalization.WORDS)
        numero = TextField(icon=icons.NUMBERS,hint_text="Numero fermata",border_radius=15,keyboard_type="number",filled=True)

        def salva_preferito(e):
            if nome.value and numero.value:
                preferiti = pagina.client_storage.get("preferiti") or []
                dizio = {"nome": nome.value,
                         "numero": numero.value
                }
                preferiti.insert(0, dizio)
                pagina.client_storage.set("preferiti", preferiti)
                form.open = False
                carica_preferiti()
            else:
                annulla_preferito(e)

        def annulla_preferito(e):
            form.open = False
            pagina.update()

        form = BottomSheet(content=Container(padding = padding.symmetric(vertical = 0, horizontal = 20),content=Column(controls=[Text("Nuovo preferito", weight=FontWeight.W_500, size=20),Divider(thickness=0, color=colors.TRANSPARENT),nome,numero,Divider(thickness=0, color=colors.TRANSPARENT),Row(controls=[TextButton(icon=icons.CLOSE, text="Annulla", on_click=annulla_preferito),TextButton(icon=icons.CHECK, text="Salva", on_click=salva_preferito)],alignment=MainAxisAlignment.CENTER)],horizontal_alignment="center",alignment=MainAxisAlignment.CENTER)),open=True, show_drag_handle=True,enable_drag=True,use_safe_area=True,is_scroll_controlled=True)
        pagina.add(form)

    # Cambia le pagine tramite NavBar
    def cambia_pagina(e):
        if e.control.selected_index == 0:
            carica_avvisi()
        elif e.control.selected_index == 1:
            carica_preferiti()
        else:
            carica_impostazioni()
    
    # Torna alla pagina precedente
    def torna_indietro(e):
        if pagina.ultima_pagina == 0:
            carica_avvisi()
        elif pagina.ultima_pagina == 1:
            carica_preferiti()
        else:
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
    
    # Verifica avvio
    def verifica_avvio():
        avvio = pagina.client_storage.get("avvio")
        if avvio == False:
            carica_avvisi()
        elif avvio == True:
            pagina.swc_avvio.value = True
            carica_preferiti()
        else:
            pagina.client_storage.set("avvio", False)
            carica_avvisi()

    # Modifica avvio
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
        URL_GITHUB = "https://github.com/madchri/transito/"
        pagina.launch_url(URL_GITHUB)
    
    # Avvia download aggiornamento
    def avvia_download(e):
        URL_DOWNLOAD = "https://github.com/madchri/transito/releases/latest/download/transito.apk"
        pagina.launch_url(URL_DOWNLOAD)

    # Mostra la pagina Impostazioni
    def carica_impostazioni():
        pagina.ricerca = False
        pagina.ultima_pagina = 2
        layout_superiore2 = AppBar(title = Column(controls = [Row(controls = [IconButton(icon = icons.SETTINGS_OUTLINED, icon_size = 30), pagina.txt_ricerca, IconButton(icon = icons.SEARCH, icon_size = 30, tooltip = "Cerca", on_click = stampa_passaggi)])]), center_title = True, toolbar_height = 85, elevation = 0, bgcolor = colors.SURFACE)
        crd_informazioni = Card(content = Container(content = Column([ListTile(title = Text("Informazioni", size = 15)), ListTile(leading = Icon(icons.INFO_OUTLINE, color = colors.ON_BACKGROUND),title = Text("Crediti", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Dettagli sull'app"), trailing = FilledTonalButton(text = "GitHub", icon = icons.OPEN_IN_NEW, width = 118, on_click = apri_github))], spacing = 0),padding = padding.symmetric(vertical = 10, horizontal = 4)))
        crd_generali = Card(content = Container(content = Column([ListTile(title = Text("Generali", size = 15)), ListTile(leading = Icon(icons.DARK_MODE_OUTLINED, color = colors.ON_BACKGROUND),title = Text("Tema scuro", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Affatica meno la vista"), trailing = pagina.swc_tema), ListTile(leading = Icon(icons.STAR_OUTLINE, color = colors.ON_BACKGROUND), title = Text("Apri preferiti", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Apri i preferiti all'avvio"), trailing = pagina.swc_avvio)], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)))
        crd_memoria = Card(content = Container(content = Column([ListTile(title = Text("Archiviazione", size = 15)), ListTile(leading = Icon(icons.DATA_USAGE_OUTLINED, color = colors.ON_BACKGROUND), title = Text("Elimina dati", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Ripristina le impostaz."), trailing = IconButton(icon = icons.DELETE_OUTLINE, icon_size = 30, bgcolor = colors.SECONDARY_CONTAINER, icon_color = colors.ON_BACKGROUND, on_click=elimina_dati))], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)))
        pagina.clean()
        if pagina.aggiornata == False:
            pagina.add(layout_superiore2, pagina.crd_aggiorna, crd_generali, crd_memoria, crd_informazioni, pagina.navbar)
        else:
            pagina.add(layout_superiore2, crd_generali, crd_memoria, pagina.crd_aggiorna, crd_informazioni, pagina.navbar)

    # Eliminazione dati app
    def elimina_dati(e):
        pagina.client_storage.clear()
        pagina.add(SnackBar(content=Text("Dati dell'app eliminati con successo"), open=True))

    # Filtro per gli avvisi 0
    def filtro_torino(e):
        pagina.filtro = "Torino e cintura"
        pagina.chip0.selected = True
        pagina.chip1.selected = False
        carica_avvisi()

    # Filtro per gli avvisi 1
    def filtro_provincia(e):
        pagina.filtro = "Provincia e Piemonte"
        pagina.chip1.selected = True
        pagina.chip0.selected = False
        carica_avvisi()

    # Controlla gli aggiornamenti
    def verifica_aggiornamenti():
        URL_AGGIORNA = "https://api.github.com/repos/madchri/transito/releases/latest"
        try:
            risposta = get(URL_AGGIORNA).json()
            if risposta["name"] > VERSIONE:
                pagina.aggiornata = False
                pagina.alertdg = AlertDialog(title = Text("Aggiornamento", text_align = "center", weight = FontWeight.W_600), icon = Icon(icons.UPDATE), content = Text(risposta["body"]), modal = True, open = True, actions = [TextButton(text = "Non ora", icon = icons.CLOSE, on_click = chiudi_dialogo), TextButton(text = "Scarica", icon = icons.DOWNLOAD,on_click = avvia_download)], actions_alignment = MainAxisAlignment.SPACE_BETWEEN)
                pagina.navbar = NavigationBar(destinations = [NavigationDestination(icon = icons.HOME_OUTLINED, selected_icon = icons.HOME, label = "Avvisi"), NavigationDestination(icon = icons.STAR_OUTLINE, selected_icon = icons.STAR, label = "Preferiti"), NavigationDestination(icon_content = Badge(content = Icon(icons.SETTINGS_OUTLINED), small_size = 10), selected_icon_content = Badge(content = Icon(icons.SETTINGS), small_size = 10), label = "Impostaz.")], on_change = cambia_pagina, label_behavior = NavigationBarLabelBehavior.ALWAYS_SHOW)
                pagina.crd_aggiorna = Card(content = Container(content = Column([ListTile(title = Text("Aggiornamenti", size = 15)), ListTile(leading = Icon(icons.UPDATE, color = colors.ON_BACKGROUND), title = Text("Aggiorna l'app", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Versione " + risposta["name"]), trailing = FilledButton(text = "Scarica", icon = icons.DOWNLOAD, width = 122, on_click = avvia_download))], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)), color = colors.SECONDARY_CONTAINER)
                pagina.add(pagina.navbar, pagina.alertdg)
        except Exception:
            pass

    def carica_avvisi():
        pagina.ricerca = False
        pagina.ultima_pagina = 0 
        pgb_caricamento = ProgressBar(bgcolor = colors.TRANSPARENT, visible = True)
        layout_superiore0 = AppBar(title = Column(controls = [Row(controls = [IconButton(icon = icons.HOME_OUTLINED, icon_size = 30), pagina.txt_ricerca,IconButton(icon = icons.SEARCH, icon_size = 30, tooltip = "Cerca", on_click = stampa_passaggi)])]), center_title = True, toolbar_height = 85,elevation = 0,bgcolor = colors.SURFACE)
        pagina.clean()
        pagina.add(layout_superiore0, pgb_caricamento, pagina.navbar)
        if not pagina.feed_caricato:
            URL_FEED = "https://www.gtt.to.it/cms/avvisi-e-informazioni-di-servizio?format=feed"
            try:
                pagina.avvisi = parse(URL_FEED)["entries"]
                pagina.feed_caricato = True
            except Exception:
                pass
        if pagina.navbar.selected_index == 0:
            if pagina.avvisi:
                pgb_caricamento.visible = False
                layout_chips = Row([pagina.chip0, pagina.chip1], scroll = "hidden")
                pagina.add(layout_chips)
                avvisi_filtrati = [avviso for avviso in pagina.avvisi if avviso["tags"][0]["term"] == pagina.filtro or avviso["tags"][0]["term"] == "Varie"]
                for avviso in avvisi_filtrati:
                    stringhe = BeautifulSoup(avviso["summary"], features = "html.parser").findAll(string = True)
                    contenuto = "".join(stringhe).replace("Leggi tutto...", "").replace("CALCOLA IL TUO PERCORSO", "").rstrip("\n")
                    menu = ExpansionTile(title = Text(avviso["title"], weight = FontWeight.W_500, color = colors.ON_BACKGROUND),controls = [Text(contenuto, color = colors.ON_BACKGROUND)], collapsed_text_color = colors.ON_BACKGROUND, collapsed_icon_color = colors.ON_BACKGROUND, controls_padding = padding.symmetric(vertical = 15, horizontal = 15))
                    card = Card(content = Container(content = Column([menu], spacing = 0),padding = padding.symmetric(vertical = 10, horizontal = 4), border_radius = 10))
                    pagina.add(card)
            else:
                pgb_caricamento.visible = False
                pagina.add(Container(content = Text("Nessun avviso da mostrare"), padding = 50))

    def stampa_passaggi(e):
        pagina.iterazioni = 0
        ora = datetime.now()
        pagina.dati = passaggi_mato(pagina.txt_ricerca.value, ora)
        avvisi = avvisi_gtfs(pagina.gtfs, pagina.txt_ricerca.value)
        n_avvisi = len(avvisi)
        if pagina.dati:
            pagina.ricerca = True
            layout_superiore1 = AppBar(title = Column(controls = [Row(controls = [IconButton(icon = icons.ARROW_BACK, tooltip = "Indietro", icon_size = 30, on_click = torna_indietro), pagina.txt_ricerca, IconButton(icon = icons.REFRESH, icon_size = 30, tooltip = "Aggiorna", on_click = stampa_passaggi)])]), center_title = True, toolbar_height = 85, elevation = 0, bgcolor = colors.SURFACE)
            pagina.clean()
            pagina.add(layout_superiore1, pagina.navbar)

            recenti = pagina.client_storage.get("recenti") or []
            if pagina.txt_ricerca.value not in recenti:
                recenti.insert(0, str(pagina.txt_ricerca.value))
                pagina.client_storage.set("recenti", recenti)

            if n_avvisi > 0:
                contenuto = []
                for avviso in avvisi:
                    contenuto.append(Divider(thickness=0, color=colors.ON_BACKGROUND))
                    contenuto.append(ListTile(title=Text(avviso["titolo"], weight=FontWeight.W_500, color=colors.ON_SECONDARY_CONTAINER), subtitle=Text(avviso["descrizione"], color=colors.ON_SECONDARY_CONTAINER)))
                menu = ExpansionTile(leading = Icon(icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=colors.ON_BACKGROUND), title = Text(f"{n_avvisi} avvisi per questa fermata", weight = FontWeight.W_500, size=15, color = colors.ON_BACKGROUND, no_wrap = True, overflow = TextOverflow.FADE), controls = contenuto, collapsed_text_color = colors.ON_BACKGROUND,collapsed_icon_color = colors.ON_BACKGROUND)
                crd_mezzo = Card(content = Container(content = Column([menu], spacing = 0), padding = padding.symmetric(vertical = 0, horizontal = 0), border_radius = 10), show_border_on_foreground = True, color=colors.SECONDARY_CONTAINER)
                pagina.add(crd_mezzo)

            for linea_key in pagina.dati:
                linea = pagina.dati[linea_key]
                if linea["tipo"] == "TRAM":
                    icona = Icon(icons.TRAM_SHARP, size = 23, color = colors.GREEN)
                else:
                    icona = Icon(icons.DIRECTIONS_BUS, size = 23, color = colors.PRIMARY)
                passaggio = linea["arrivi"][pagina.iterazioni]
                if passaggio["minuti_restanti"] !=  False:
                    if passaggio["realtime"]:
                        colore = colors.GREEN
                    else:
                        colore = colors.ON_BACKGROUND
                    direzione = ListTile(title = Text("Direzione", weight = FontWeight.W_500), subtitle = Row([Text(linea["direzione"], no_wrap = True)],auto_scroll = True, scroll = "hidden"))
                    accessibilita = ListTile(title = Text("Accessibilità", weight = FontWeight.W_500), subtitle = Row([Text(linea["accessibilita"], no_wrap = True)],auto_scroll = True, scroll = "hidden"))
                    menu = ExpansionTile(leading = icona, title = Text(linea_key, size = 23, weight = FontWeight.W_500, color = colors.ON_BACKGROUND, no_wrap = True, overflow = TextOverflow.FADE), controls = [direzione, accessibilita], collapsed_text_color = colors.PRIMARY,collapsed_icon_color = colors.PRIMARY, trailing = Row([Text(passaggio["minuti_restanti"], color = colore, size = 23)],alignment = MainAxisAlignment.END, tight = True))
                    crd_mezzo = Card(content = Container(content = Column([menu], spacing = 0),padding = padding.symmetric(vertical = 10, horizontal = 4),border_radius = 10), show_border_on_foreground = True)
                    pagina.add(crd_mezzo)
            pagina.iterazioni +=  1
            pagina.add(Divider(thickness = 0), pagina.more)
        else:
            snb_noinfo = SnackBar(content = Text("Nessuna informazione disponibile"), open = True)
            pagina.add(snb_noinfo)

    def mostra_successivi(e):
        try:
            pagina.auto_scroll = True
            pagina.remove(pagina.more)
            for linea_key in pagina.dati:
                linea = pagina.dati[linea_key]
                if linea["tipo"] == "TRAM":
                    icona = Icon(icons.TRAM_SHARP, size = 23, color = colors.GREEN)
                else:
                    icona = Icon(icons.DIRECTIONS_BUS, size = 23, color = colors.PRIMARY)
                passaggio = linea["arrivi"][pagina.iterazioni]
                if passaggio["minuti_restanti"] !=  False:
                    if passaggio["realtime"]:
                        colore = colors.GREEN
                    else:
                        colore = colors.ON_BACKGROUND
                    direzione = ListTile(title = Text("Direzione", weight = FontWeight.W_500), subtitle = Row([Text(linea["direzione"], no_wrap = True)],auto_scroll = True, scroll = "hidden"))
                    accessibilita = ListTile(title = Text("Accessibilità", weight = FontWeight.W_500), subtitle = Row([Text(linea["accessibilita"], no_wrap = True)],auto_scroll = True, scroll = "hidden"))
                    menu = ExpansionTile(leading = icona, title = Text(linea_key, size = 23, weight = FontWeight.W_500, color = colors.ON_BACKGROUND, no_wrap = True, overflow = TextOverflow.FADE), controls = [direzione, accessibilita], collapsed_text_color = colors.PRIMARY,collapsed_icon_color = colors.PRIMARY, trailing = Row([Text(passaggio["minuti_restanti"], color = colore, size = 23)],alignment = MainAxisAlignment.END, tight = True))
                    crd_mezzo = Card(content = Container(content = Column([menu], spacing = 0),padding = padding.symmetric(vertical = 10, horizontal = 4),border_radius = 10), show_border_on_foreground = True)
                    pagina.add(crd_mezzo)
            pagina.iterazioni +=  1
            pagina.add(Divider(thickness = 0), pagina.more)
            pagina.auto_scroll = False
        except Exception:
            pagina.auto_scroll = False

    # Elementi layout globali
    pagina.dati = []
    pagina.iterazioni = 0
    pagina.alertdg = AlertDialog()
    pagina.swc_tema = Switch(on_change = cambia_tema, value = True)
    pagina.swc_avvio = Switch(on_change = cambia_avvio, value = False)
    pagina.more = IconButton(icon = icons.KEYBOARD_ARROW_DOWN, icon_size = 30, bgcolor = colors.SECONDARY_CONTAINER, icon_color = colors.ON_BACKGROUND, on_click = mostra_successivi)
    pagina.txt_ricerca = TextField(filled = True, hint_text = "Cerca fermata", text_align = "center", text_vertical_align = 1.0, keyboard_type = "number", border_radius = 100, height = 56.0, expand = True, autofocus = False, on_submit = stampa_passaggi)
    pagina.navbar = NavigationBar(destinations = [NavigationDestination(icon = icons.HOME_OUTLINED, selected_icon = icons.HOME, label = "Avvisi"), NavigationDestination(icon = icons.STAR_OUTLINE, selected_icon = icons.STAR, label = "Preferiti"), NavigationDestination(icon = icons.SETTINGS_OUTLINED, selected_icon = icons.SETTINGS, label = "Impostaz.")], on_change = cambia_pagina, label_behavior = NavigationBarLabelBehavior.ALWAYS_SHOW)
    pagina.crd_aggiorna = Card(content = Container(content = Column([ListTile(title = Text("Aggiornamenti", size = 15)), ListTile(leading = Icon(icons.UPDATE, color = colors.ON_BACKGROUND), title = Text("App aggiornata", weight = FontWeight.W_600, color = colors.ON_BACKGROUND), subtitle = Text("Versione " + VERSIONE), trailing = IconButton(icon = icons.CHECK, icon_size = 30, bgcolor = colors.SECONDARY_CONTAINER, icon_color = colors.ON_BACKGROUND))], spacing = 0), padding = padding.symmetric(vertical = 10, horizontal = 4)))
    pagina.chip0 = Chip(label = Text("Torino e cintura"), show_checkmark = False, shape = RoundedRectangleBorder(radius = 100), on_click = filtro_torino, selected = True, disabled = False)
    pagina.chip1 = Chip(label = Text("Provincia e Piemonte"), show_checkmark = False, shape = RoundedRectangleBorder(radius = 100), on_click = filtro_provincia, selected = False, disabled = False)

    # Caricamento iniziale
    verifica_tema()
    verifica_avvio()
    pagina.gtfs = ottieni_gtfs()
    verifica_aggiornamenti()

app(main)
