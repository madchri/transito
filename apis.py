import flet as ft
from feedparser import parse
from bs4 import BeautifulSoup
from datetime import datetime
from requests import post, get

def get_rss(): 
    try:
        entries = parse("https://www.gtt.to.it/cms/avvisi-e-informazioni-di-servizio?format=feed")["entries"]
    except Exception:
        return None
    elements = ft.Column()
    for entry in entries:
        if entry["tags"][0]["term"] in ["Torino e cintura", "Varie"]:
            text = BeautifulSoup(entry["summary"], features="html.parser").get_text().replace("Leggi tutto...", "").rstrip("\n")
            elements.controls.append(ft.Card(content=ft.ExpansionTile(title=ft.Text(entry["title"], weight=ft.FontWeight.W_500),controls=[ft.Text(text), ft.Divider(thickness=0, color=ft.colors.TRANSPARENT)],controls_padding=ft.padding.symmetric(horizontal=20),tile_padding=ft.padding.symmetric(vertical=10, horizontal=20),shape=ft.RoundedRectangleBorder(radius=10),collapsed_shape=ft.RoundedRectangleBorder(radius=10))))
    return elements

def get_updates(version):
    try:
        response = get("https://api.github.com/repos/madchri/transito/releases/latest").json()
        return response["body"] if response["name"] > version else None
    except Exception:
        return None

def get_data(stop_code):
    query = """
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
    """
    try:
        response = post("https://plan.muoversiatorino.it/otp/routers/mato/index/graphql", headers={"Content-Type": "application/json"}, json={"query": query, "variables": {"id": f"gtt:{stop_code}", "timeRange": 3600, "numberOfDepartures": 3600}})
        output = response.json()["data"]["stop"]["stoptimesWithoutPatterns"]
    except Exception:
        return {}

    vehicles = {}
    current_time = datetime.now()
    for line in output:
        line_name = line["trip"]["pattern"]["route"]["shortName"]
        time, minutes_remaining = convert_time(line["realtimeArrival"], current_time)
        if line_name not in vehicles:
            vehicles[line_name] = {"type": line["trip"]["pattern"]["route"]["mode"], "arrivals": []}
        vehicles[line_name]["arrivals"].append({"time": time, "realtime": line["realtime"], "minutes_remaining": minutes_remaining})
    return vehicles

def convert_time(time, current_time):
    minutes_remaining = (time - (current_time - datetime(current_time.year, current_time.month, current_time.day)).seconds) // 60
    return f"{(time // 3600) % 24:02}:{(time % 3600) // 60:02}", minutes_remaining

def get_times(code, simple_time):
    data = get_data(code)
    elements = ft.Column()
    for line_key, line in data.items():
        leading_icon = ft.Icon(ft.icons.TRAM_SHARP, size=23, color=ft.colors.GREEN) if line["type"] == "TRAM" else ft.Icon(ft.icons.DIRECTIONS_BUS, size=22, color=ft.colors.PRIMARY)
        first_arrival = line["arrivals"][0]
        trailing_text = ft.Text("ora " if simple_time and first_arrival["minutes_remaining"] == 0 else str(first_arrival["minutes_remaining"]) + " min " if simple_time else first_arrival["time"] + " ",size=22,weight=ft.FontWeight.W_500,color=ft.colors.GREEN if first_arrival["realtime"] else None)
        card = ft.Card(content=ft.ExpansionTile(leading=leading_icon,title=ft.Text(line_key, size=22, weight=ft.FontWeight.W_500),trailing=trailing_text,shape=ft.RoundedRectangleBorder(radius=10),collapsed_shape=ft.RoundedRectangleBorder(radius=10),controls_padding=ft.padding.symmetric(horizontal=7),tile_padding=ft.padding.symmetric(vertical=10, horizontal=20),))
        for arrival in line["arrivals"][1:]:
            card.content.controls.append(ft.ListTile(title=ft.Text("tra " + str(arrival["minutes_remaining"]) + " minuti", weight=ft.FontWeight.W_500, size=15, color=ft.colors.GREEN if arrival["realtime"] else None),trailing=ft.Text(arrival["time"], weight=ft.FontWeight.W_500, size=15, color=ft.colors.GREEN if arrival["realtime"] else None)))
        card.content.controls.append(ft.Divider(thickness=0, color=ft.colors.TRANSPARENT))
        elements.controls.append(card)
    return elements
