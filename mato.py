from requests import post

# Recupera i passaggi alla fermata
def passaggi(fermata, ora):
    richiesta_id = {
        "id": "q01",
        "query": """
            query StopRoutes($id_0: String!) {
                stop(id:$id_0) {
                    id
                }
            }
        """,
        "variables": {
            "id_0": f"gtt:{fermata}"
        }
    }
    URL_API = "https://plan.muoversiatorino.it/otp/routers/mato/index/graphql"
    try:
        risposta_id = post(URL_API, headers = {"Content-Type": "application/json"}, json = richiesta_id)
        id_fermata = risposta_id.json()["data"]["stop"]["id"]
    except Exception:
        return tuple()
    richiesta_dati = {
        "id": "q02",
        "query": """
            query StopPageContentContainer_StopRelayQL($id_0:ID!,$startTime_1:Long!,$timeRange_2:Int!,$numberOfDepartures_3:Int!) {
                node(id:$id_0) {
                    ...F2
                }
            }
            fragment F1 on Stoptime {
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
            fragment F2 on Stop {
                _stoptimesWithoutPatterns1WnWVl:stoptimesWithoutPatterns(
                    startTime:$startTime_1,
                    timeRange:$timeRange_2,
                    numberOfDepartures:$numberOfDepartures_3,
                    omitCanceled:true
                ) {
                    ...F1
                }
            }
        """,
        "variables": {
            "id_0": id_fermata,
            "startTime_1": ora.timestamp(),
            "timeRange_2": 3600,
            "numberOfDepartures_3": 3600
        }
    }
    try:
        risposta_dati = post(URL_API, headers = {"Content-Type": "application/json"}, json = richiesta_dati)
        output = risposta_dati.json()["data"]["node"]["_stoptimesWithoutPatterns1WnWVl"]
        return output
    except Exception:
        return tuple()

# Calcola gli orari a partire dai secondi
def orari(secondiRT, ora):
    oraRT = (secondiRT // 3600) % 24
    minutiRT = (secondiRT % 3600) // 60
    if oraRT < 10:
        oraRT = '0' + str(oraRT)
    if minutiRT < 10:
        minutiRT = '0' + str(minutiRT)
    orarioRT = str(oraRT) + ':' + str(minutiRT)
    minuti_restanti = abs((ora.hour * 3600) + (ora.minute * 60) + ora.second - secondiRT) // 60
    if minuti_restanti == 0:
        tempo = "ora"
    else:
        tempo = str(minuti_restanti) + " min"
    return (tempo, orarioRT)
