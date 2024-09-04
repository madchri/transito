import flet as ft
from apis import get_rss, get_updates, get_times

def main(page):

    VERSION = "2.0.1"
    page.title = "TransiTO"
    page.scroll = ft.ScrollMode.HIDDEN

    def open_drawer(e):
        page.open(page.drawer)
    
    def change_drawer(e):
        page.navigation_bar.selected_index = page.drawer.selected_index
        page.close(page.drawer)
        change_pagelet(e)

    def change_pagelet(e):
        if page.navigation_bar.selected_index == 0:
            nonlocal rss_loaded
            nonlocal pagelet1_content
            if not rss_loaded:
                pagelet.content = pagelet1_content
                page.floating_action_button.visible = False
                page.floating_action_button.update()
                pagelet.update()
                pagelet1_content = get_rss()
                rss_loaded = True
            if page.navigation_bar.selected_index == 0:
                pagelet.content = pagelet1_content
                page.floating_action_button.visible = False
        elif page.navigation_bar.selected_index == 1:
            pagelet.content = scan_favs()
        else:
            pagelet.content = pagelet3_content
            page.floating_action_button.visible = False
        page.drawer.selected_index = page.navigation_bar.selected_index
        page.appbar.title.controls[0].icon = ft.icons.MENU
        page.appbar.title.controls[0].on_click = open_drawer
        page.appbar.title.controls[2].icon = ft.icons.SEARCH
        page.appbar.title.controls[2].on_click = start_search
        page.update()
    
    def add_fav(e):

        def save_fav(e):
            if name.value and code.value:
                favs = page.client_storage.get("fav_list") or []
                favs.insert(0, {"name": name.value, "code": str(code.value)})
                page.client_storage.set("fav_list", favs)
                pagelet.content = scan_favs()
                form.open = False
                page.update()
            else:
                quit_form(e)

        def quit_form(e):
            form.open = False
            form.update()

        name = ft.TextField(icon=ft.icons.TEXT_FIELDS, hint_text="Nome (a piacere)", border_radius=15, filled=True, autofocus=True, capitalization=ft.TextCapitalization.WORDS)
        code = ft.TextField(icon=ft.icons.NUMBERS, hint_text="Numero fermata", border_radius=15, keyboard_type="number", filled=True, on_submit=save_fav)
        form = ft.BottomSheet(content=ft.Container(padding = ft.padding.symmetric(vertical = 0, horizontal = 20),content=ft.Column(controls=[ft.Text("Nuovo preferito", weight=ft.FontWeight.W_500, size=20),ft.Divider(thickness=0, color=ft.colors.TRANSPARENT),name,code,ft.Divider(thickness=0, color=ft.colors.TRANSPARENT),ft.Row(controls=[ft.TextButton(icon=ft.icons.CLOSE, text="Annulla", on_click=quit_form),ft.TextButton(icon=ft.icons.CHECK, text="Salva", on_click=save_fav)],alignment=ft.MainAxisAlignment.CENTER)],horizontal_alignment="center",alignment=ft.MainAxisAlignment.CENTER)),open=True, show_drag_handle=True,enable_drag=True,use_safe_area=True,is_scroll_controlled=True)
        page.add(form)
    
    def search_fav(e):
        page.appbar.title.controls[1].value = e.control.trailing.value.rstrip(' ')
        start_search(e)

    def scan_favs():
        favs = page.client_storage.get("fav_list")
        elements = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        if favs:
            for fav in favs:
                card = ft.Card(ft.ListTile(leading = ft.Icon(ft.icons.LOCATION_ON_OUTLINED, size=22),title = ft.Text(fav["name"], weight = ft.FontWeight.W_500, size = 22), trailing = ft.Text(fav["code"] + " ", weight = ft.FontWeight.W_500, size = 22), content_padding=ft.padding.symmetric(vertical=10, horizontal=20), shape=ft.RoundedRectangleBorder(radius=10), on_click=search_fav))
                elements.controls.append(card)
        else:
            elements.controls = [ft.Container(height=200), ft.Text("Nessun preferito", weight=ft.FontWeight.W_500, size=18), ft.Text("Prova ad aggiungerne uno")]
        page.drawer.selected_index = 1
        page.navigation_bar.selected_index = 1
        page.floating_action_button.visible = True
        return elements

    def start_search(e):
        simple_time = page.client_storage.get("simple_time")
        data = get_times(page.appbar.title.controls[1].value, simple_time)
        if data.controls:
            pagelet.content = data
            page.navigation_bar.selected_index = 1
            page.floating_action_button.visible = False
            page.appbar.title.controls[0].icon = ft.icons.ARROW_BACK
            page.appbar.title.controls[0].on_click = change_pagelet
            page.appbar.title.controls[2].icon = ft.icons.REFRESH
            page.update()
        else:
            page.add(ft.SnackBar(content=ft.Text("Nessuna informazione disponibile", color=ft.colors.ON_ERROR_CONTAINER), open=True, bgcolor=ft.colors.ERROR_CONTAINER))

    def change_theme(e):
        page.client_storage.set("light_theme", not e.control.value)
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        page.update()

    def change_start(e):
        page.client_storage.set("fav_start", e.control.value)
    
    def change_time(e):
        page.client_storage.set("simple_time", e.control.value)

    def delete_data(e):
        page.client_storage.clear()
        pagelet3_content.controls[7].trailing = ft.Icon(ft.icons.CHECK, size=30, color=ft.colors.GREEN)
        pagelet.update()
        pagelet3_content.controls[7].trailing = ft.Icon(ft.icons.ARROW_FORWARD_IOS_ROUNDED, size=25)
    
    def close_dialog(e):
        dialog.open = False
        page.update()

    def open_github(e):
        GITHUB_URL = "https://github.com/madchri/transito/"
        page.launch_url(GITHUB_URL)
    
    def start_download(e):
        DOWNLOAD_URL = "https://github.com/madchri/transito/releases/latest/download/transito.apk"
        page.launch_url(DOWNLOAD_URL)
    
    pagelet3_content = ft.Column(controls=[ft.Text("", size=1),ft.Container(content=ft.Row(controls=[ft.Text("Aspetto", color=ft.colors.PRIMARY, size=14)]), padding=ft.padding.symmetric(horizontal=16)),ft.ListTile(title=ft.Text("Tema scuro", weight=ft.FontWeight.W_500), subtitle=ft.Text("Affatica meno la vista"), trailing=ft.Switch(on_change=change_theme)),ft.ListTile(title=ft.Text("Cerca all'avvio", weight=ft.FontWeight.W_500), subtitle=ft.Text("Apre subito la ricerca"), trailing=ft.Switch(on_change=change_start)),ft.ListTile(title=ft.Text("Orari semplici", weight=ft.FontWeight.W_500), subtitle=ft.Text("Mostra minuti all'arrivo"), trailing=ft.Switch(on_change=change_time)),ft.Text("", size=1),ft.Container(content=ft.Row(controls=[ft.Text("Archiviazione", color=ft.colors.PRIMARY, size=14)]), padding=ft.padding.symmetric(horizontal=16)),ft.ListTile(title=ft.Text("Elimina dati", weight=ft.FontWeight.W_500), subtitle=ft.Text("Rimuove i dati dell'app"), trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS_ROUNDED, size=25), on_click=delete_data),ft.Text("", size=1),ft.Container(content=ft.Row(controls=[ft.Text("Informazioni", color=ft.colors.PRIMARY, size=14)]), padding=ft.padding.symmetric(horizontal=16)),ft.ListTile(title=ft.Text("GitHub", weight=ft.FontWeight.W_500), subtitle=ft.Text("Scopri ulteriori dettagli"), trailing=ft.Icon(ft.icons.OPEN_IN_NEW_ROUNDED, size=25), on_click=open_github)])

    # Check selected theme
    light_theme = page.client_storage.get("light_theme")
    page.theme_mode = ft.ThemeMode.LIGHT if light_theme else ft.ThemeMode.DARK
    pagelet3_content.controls[2].trailing.value = not light_theme

    # Check selected time format
    simple_time = page.client_storage.get("simple_time")
    pagelet3_content.controls[4].trailing.value = simple_time

    pagelet1_content = ft.ProgressBar(bgcolor=ft.colors.TRANSPARENT)

    pagelet = ft.Container(content=ft.ProgressBar(bgcolor=ft.colors.TRANSPARENT), alignment=ft.alignment.center)

    page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD, text="Aggiungi", visible=False, shape=ft.StadiumBorder(), on_click=add_fav)
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_FLOAT

    page.navigation_bar = ft.NavigationBar(destinations=[ft.NavigationBarDestination(icon=ft.icons.NEWSPAPER_OUTLINED, selected_icon=ft.icons.NEWSPAPER, label="Notizie"),ft.NavigationBarDestination(icon=ft.icons.SEARCH_OUTLINED, selected_icon=ft.icons.SEARCH, label="Ricerca"),ft.NavigationBarDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="Impost.")],label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,on_change=change_pagelet)

    page.appbar = ft.AppBar(title=ft.Row(controls=[ft.IconButton(icon=ft.icons.MENU, icon_size=30, on_click=open_drawer),ft.TextField(filled=True, hint_text="Cerca fermata", text_vertical_align = 1.0, text_align=ft.TextAlign.CENTER,keyboard_type=ft.KeyboardType.NUMBER, border_radius=100, height=56.0,expand=True, on_submit=start_search),ft.IconButton(icon=ft.icons.SEARCH, icon_size=30, on_click=start_search)]),center_title=True,automatically_imply_leading=False,toolbar_height=85)

    page.drawer = ft.NavigationDrawer(controls=[ft.Container(height=40),ft.ListTile(title=ft.Text(page.title, size=20, weight=ft.FontWeight.W_500), subtitle=ft.Text(f"Versione {VERSION}")),ft.Divider(thickness=0),ft.Text("", size=3),ft.NavigationDrawerDestination(icon_content=ft.Icon(ft.icons.NEWSPAPER_OUTLINED), label="Notizie", selected_icon=ft.icons.NEWSPAPER),ft.NavigationDrawerDestination(icon_content=ft.Icon(ft.icons.SEARCH_OUTLINED), label="Ricerca", selected_icon=ft.icons.SEARCH),ft.NavigationDrawerDestination(icon_content=ft.Icon(ft.icons.SETTINGS_OUTLINED), label="Impostazioni", selected_icon=ft.icons.SETTINGS)],on_change=change_drawer)

    page.add(pagelet)

    # Check selected start page
    rss_loaded = False
    fav_start = page.client_storage.get("fav_start")
    pagelet3_content.controls[3].trailing.value = fav_start
    if fav_start:
        pagelet.content = scan_favs()
        page.update()
    else:
        pagelet1_content = get_rss()
        pagelet.content = pagelet1_content
        rss_loaded = True
        if page.navigation_bar.selected_index == 0:
            pagelet.update()
    
    # Check for updates
    body = get_updates(VERSION)
    if body:
        dialog = ft.AlertDialog(title = ft.Text("Aggiornamento", text_align = ft.TextAlign.CENTER, weight = ft.FontWeight.W_500), icon = ft.Icon(ft.icons.UPDATE), content = ft.Text(body), modal = True, open = True, actions = [ft.TextButton(text = "Non ora", icon = ft.icons.CLOSE, on_click=close_dialog), ft.TextButton(text = "Scarica", icon = ft.icons.DOWNLOAD, on_click=start_download)])
        card = ft.Card(content = ft.ListTile(title = ft.Text("Aggiornamento", weight = ft.FontWeight.W_500), trailing = ft.FilledButton(text = "Scarica", icon = ft.icons.DOWNLOAD, width = 123, on_click = start_download), bgcolor=ft.colors.SECONDARY_CONTAINER, content_padding=ft.padding.symmetric(vertical=10, horizontal=20), shape=ft.RoundedRectangleBorder(radius=10)))
        page.navigation_bar.destinations[2].icon_content = ft.Badge(content = ft.Icon(ft.icons.SETTINGS_OUTLINED), small_size = 10)
        page.navigation_bar.destinations[2].selected_icon_content = ft.Badge(content = ft.Icon(ft.icons.SETTINGS), small_size = 10)
        page.drawer.controls[6].icon_content = ft.Badge(content = ft.Icon(ft.icons.SETTINGS_OUTLINED), small_size = 10)
        page.drawer.controls[6].selected_icon_content = ft.Badge(content = ft.Icon(ft.icons.SETTINGS), small_size = 10)
        pagelet3_content.controls.insert(0, card)
        page.navigation_bar.update()
        page.drawer.update()
        page.add(dialog)

ft.app(main)
