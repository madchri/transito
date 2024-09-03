import flet as ft
from feedparser import parse
from bs4 import BeautifulSoup
from datetime import datetime
from requests import post, get

def get_rss(): 
    FEED_URL="https://www.gtt.to.it/cms/avvisi-e-informazioni-di-servizio?format=feed"
    try:
        entries = parse(FEED_URL)["entries"]
    except Exception:
        return
    elements = ft.Column()
    for entry in entries:
        if entry["tags"][0]["term"] == "Torino e cintura" or entry["tags"][0]["term"] == "Varie":
            soup = BeautifulSoup(entry["summary"], features="html.parser").findAll(string=True)
            text = "".join(soup).replace("Leggi tutto...", "").replace("CALCOLA IL TUO PERCORSO", "").rstrip("\n")
            card = ft.Card(content=ft.ExpansionTile(title=ft.Text(entry["title"], weight=ft.FontWeight.W_500), controls=[ft.Text(text), ft.Divider(thickness=0, color=ft.colors.TRANSPARENT), ft.Divider(thickness=0, color=ft.colors.TRANSPARENT)], controls_padding=ft.padding.symmetric(vertical=0, horizontal=20), tile_padding=ft.padding.symmetric(vertical=10, horizontal=20), shape=ft.RoundedRectangleBorder(radius=10), collapsed_shape=ft.RoundedRectangleBorder(radius=10)))
            elements.controls.append(card)
    return elements

def get_updates(version):
    UPDATE_URL = "https://api.github.com/repos/madchri/transito/releases/latest"
    try:
        response = get(UPDATE_URL).json()
        if response["name"] > version:
            return response["body"]
    except Exception:
        pass

def get_data(stop_code):
    API_URL = "https://plan.muoversiatorino.it/otp/routers/mato/index/graphql"
    request = {
        "query": """
            query StopInfo($id:String!,$timeRange:Int!,$numberOfDepartures:Int!) {
                stop(id:$id) {
                    stoptimesWithoutPatterns(timeRange:$timeRange,numberOfDepartures:$numberOfDepartures) {
                        realtime
                        realtimeArrival
                        trip {
                            pattern {
                                route {
                                    mode
                                    shortName
                                }
                            }
                        }
                    }
                }
            }
        """,
        "variables": {
            "id": f"gtt:{stop_code}",
            "timeRange": 3600,
            "numberOfDepartures": 3600
        }
    }

    try:
        response = post(API_URL, headers = {"Content-Type": "application/json"}, json = request)
        output = response.json()["data"]["stop"]["stoptimesWithoutPatterns"]
    except Exception:
        output = {}

    vehicles = {}
    current_time = datetime.now()
    for line in output:
        line_name = line["trip"]["pattern"]["route"]["shortName"]
        time, minutes_remaining = convert_time(line["realtimeArrival"], current_time)
        if line_name not in vehicles:
            vehicles[line_name] = {
                "type": line["trip"]["pattern"]["route"]["mode"],
                "arrivals": []
            }
        arrival = {
            "time": time,
            "realtime" : line["realtime"],
            "minutes_remaining": minutes_remaining
        }
        vehicles[line_name]["arrivals"].append(arrival)
    return vehicles

def convert_time(time, current_time):
    day_start = datetime(current_time.year, current_time.month, current_time.day)
    current_seconds = int((current_time - day_start).total_seconds())
    minutes_remaining = (time - current_seconds) // 60
    hour = (time // 3600) % 24
    minutes = (time % 3600) // 60
    time_formatted = f"{hour:02}:{minutes:02}"
    return time_formatted, minutes_remaining

def get_times(code, simple_time):
    data = get_data(code)
    elements = ft.Column()
    for line_key in data:
        card_controls = []
        line = data[line_key]
        card = ft.Card(content=ft.ExpansionTile(leading = ft.Icon(ft.icons.DIRECTIONS_BUS, size = 22, color = ft.colors.PRIMARY), title = ft.Text(line_key, size = 22, weight = ft.FontWeight.W_500), trailing = ft.Text(line["arrivals"][0]["time"] + " ", size=22, weight=ft.FontWeight.W_500), shape=ft.RoundedRectangleBorder(radius=10), collapsed_shape=ft.RoundedRectangleBorder(radius=10), controls_padding=ft.padding.symmetric(vertical=0, horizontal=7), tile_padding=ft.padding.symmetric(vertical=10, horizontal=20)))
        if line["type"] == "TRAM":
            card.content.leading = ft.Icon(ft.icons.TRAM_SHARP, size = 23, color = ft.colors.GREEN)
        if simple_time:
            card.content.trailing = ft.Text(str(line["arrivals"][0]["minutes_remaining"]) + " min ", size=22, weight=ft.FontWeight.W_500)
        if line["arrivals"][0]["minutes_remaining"] == 0 and simple_time:
            card.content.trailing = ft.Text("ora ", size=22, weight=ft.FontWeight.W_500)
        if line["arrivals"][0]["realtime"]:
            card.content.trailing.color = ft.colors.GREEN
        for i in range(1, len(line["arrivals"])):
            tile = ft.ListTile(title=ft.Text("tra " + str(line["arrivals"][i]["minutes_remaining"]) + " minuti", weight=ft.FontWeight.W_500, size=15), trailing=ft.Text(line["arrivals"][i]["time"], weight=ft.FontWeight.W_500, size=15))
            if line["arrivals"][i]["realtime"]:
                tile.title.color = ft.colors.GREEN
                tile.trailing.color = ft.colors.GREEN
            card_controls.append(tile)
        card_controls.append(ft.Divider(thickness=0, color=ft.colors.TRANSPARENT))
        card.content.controls = card_controls
        elements.controls.append(card)
    return elements
