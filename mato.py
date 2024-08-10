from requests import post
from datetime import datetime

def passaggi_mato(fermata, ora):
    URL_API = "https://plan.muoversiatorino.it/otp/routers/mato/index/graphql"
    richiesta_dati = {
        "id": "q02",
        "query": """
            query StopPageContentContainer_StopRelayQL($id_0:String!,$startTime_1:Long!,$timeRange_2:Int!,$numberOfDepartures_3:Int!) {
                stop(id:$id_0) {
                    stoptimesWithoutPatterns(startTime:$startTime_1,timeRange:$timeRange_2,numberOfDepartures:$numberOfDepartures_3,omitCanceled:true) {
                        realtime
                        realtimeArrival
                        trip {
                            tripHeadsign
                            wheelchairAccessible
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
            "id_0": f"gtt:{fermata}",
            "startTime_1": int(ora.timestamp() - 30),
            "timeRange_2": 86400,
            "numberOfDepartures_3": 86400
        }
    }

    try:
        risposta_dati = post(URL_API, headers = {"Content-Type": "application/json"}, json = richiesta_dati)
        output = risposta_dati.json()["data"]["stop"]["stoptimesWithoutPatterns"]
    except Exception:
        return {}

    mezzi = {}
    for linea in output:
        nome_linea = linea["trip"]["pattern"]["route"]["shortName"]
        orarioRT, minuti_restanti = converti_orario(linea["realtimeArrival"], ora)

        if nome_linea not in mezzi:
            if linea["trip"]["wheelchairAccessible"] == "POSSIBLE":
                accessibile = "ACCESSIBILE AI DISABILI"
            else:
                accessibile = "NON ACCESSIBILE AI DISABILI"
            mezzi[nome_linea] = {
                "tipo": linea["trip"]["pattern"]["route"]["mode"],
                "direzione": linea["trip"]["tripHeadsign"],
                "accessibilita" : accessibile,
                "arrivi": []
            }
        
        arrivo = {
            "orario": orarioRT,
            "realtime" : linea["realtime"],
            "minuti_restanti": minuti_restanti
        }
        mezzi[nome_linea]["arrivi"].append(arrivo)

    return mezzi

def converti_orario(secondiRT, ora):
    inizio_giornata = datetime(ora.year, ora.month, ora.day)
    secondi_correnti = int((ora - inizio_giornata).total_seconds())
    
    minuti_restanti = (secondiRT - secondi_correnti) // 60

    oraRT = (secondiRT // 3600) % 24
    minutiRT = (secondiRT % 3600) // 60
    orarioRT = f"{oraRT:02}:{minutiRT:02}"

    if minuti_restanti < 0:
        minuti_restanti = False
    elif minuti_restanti == 0:
        minuti_restanti = "1 min"
    elif minuti_restanti < 10:
        minuti_restanti = f"{minuti_restanti} min"
    else:
        minuti_restanti = orarioRT
    
    return orarioRT, minuti_restanti
