import requests
import datetime

# === Credenciales ===


# === Endpoints Strava ===
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ACTIVITY_URL = "https://www.strava.com/api/v3/activities/{id}"

def refresh_access_token():
    """Renueva el access token con el refresh token"""
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_activities(access_token, after, before):
    """Descarga actividades entre dos fechas"""
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "after": int(after.timestamp()),
        "before": int(before.timestamp()),
        "per_page": 20
    }
    r = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    r.raise_for_status()
    return r.json()

def get_activity_details(access_token, activity_id):
    """Obtiene detalles completos de una actividad, incluyendo laps"""
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(ACTIVITY_URL.format(id=activity_id), headers=headers, params={"include_all_efforts": "true"})
    r.raise_for_status()
    return r.json()

def pace_from_speed(speed_m_s):
    if not speed_m_s or speed_m_s == 0:
        return "-"
    pace_sec = 1000 / speed_m_s
    return f"{int(pace_sec//60)}:{int(pace_sec%60):02d}/km"

def format_report(act):
    fecha = datetime.datetime.strptime(act["start_date_local"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y")
    total_dist = act["distance"] / 1000
    total_time = str(datetime.timedelta(seconds=act["elapsed_time"]))
    avg_pace = pace_from_speed(act["average_speed"])

    report = f"{fecha}\n\n"

    if "laps" in act:
        # Warmup: primera lap
        warmup = act["laps"][0]
        report += f"Warmup: {warmup['distance']/1000:.2f}km | {str(datetime.timedelta(seconds=warmup['elapsed_time']))} | {pace_from_speed(warmup['average_speed'])}\n"

        # Series intermedias
        for lap in act["laps"][1:-1]:
            report += f"{lap['distance']/1000:.2f} ({str(datetime.timedelta(seconds=lap['elapsed_time']))} - {pace_from_speed(lap['average_speed'])})\n"

        # Cooldown: última lap
        cooldown = act["laps"][-1]
        report += f"Cooldown: {cooldown['distance']/1000:.2f}km | {str(datetime.timedelta(seconds=cooldown['elapsed_time']))} | {pace_from_speed(cooldown['average_speed'])}\n"

    report += f"Distancia Total: {total_dist:.2f}km\n"
    report += f"Tiempo Total: {total_time}\n"
    report += f"Pace Promedio: {avg_pace}\n"
    return report

def main():
    access_token = refresh_access_token()

    # Rango del 1 de octubre de 2025
    after = datetime.datetime(2025, 10, 1, 0, 0, 0)
    before = datetime.datetime(2025, 10, 2, 0, 0, 0)

    acts = get_activities(access_token, after, before)

    # Filtramos solo las corridas (Run)
    runs = [a for a in acts if a["type"] == "Run"]

    if not runs:
        print("No se encontraron corridas para esa fecha")
        return

    activity_id = runs[0]["id"]
    details = get_activity_details(access_token, activity_id)
    print(format_report(details))

if __name__ == "__main__":
    main()
