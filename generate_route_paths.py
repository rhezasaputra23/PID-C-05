
import json
import time
import math
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode

# ============================================================
# KONFIGURASI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "routes"

STOPS_FILE = DATA_DIR / "stops.json"
ROUTES_FILE = DATA_DIR / "routes.json"
OUTPUT_FILE = DATA_DIR / "route_paths.json"

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

# ============================================================
# FUNGSI BANTU
# ============================================================

def haversine_m(lat1, lon1, lat2, lon2):
    """Menghitung jarak antara dua koordinat dalam meter."""
    radius = 6371000

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def request_osrm(start, end):
    """
    Mengambil geometri jalan dari OSRM.
    start dan end menggunakan format:
    {"latitude": ..., "longitude": ...}
    """

    start_coordinate = (
        f"{start['longitude']},{start['latitude']}"
    )

    end_coordinate = (
        f"{end['longitude']},{end['latitude']}"
    )

    coordinates = f"{start_coordinate};{end_coordinate}"

    params = urlencode({
        "overview": "full",
        "geometries": "geojson",
        "steps": "false"
    })

    url = f"{OSRM_URL}/{coordinates}?{params}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PID-C-05-FleetTelematics/1.0"
        }
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))

            if result.get("code") != "Ok":
                raise RuntimeError(
                    f"OSRM tidak menemukan rute: {result.get('code')}"
                )

            route = result["routes"][0]
            geometry = route["geometry"]

            if geometry["type"] != "LineString":
                raise RuntimeError("Geometri bukan LineString.")

            if len(geometry["coordinates"]) < 2:
                raise RuntimeError("Koordinat geometri tidak mencukupi.")

            return {
                "geometry": geometry,
                "distance_m": round(route["distance"], 2),
                "duration_s": round(route["duration"], 2),
                "start_snap_distance_m": round(
                    result["waypoints"][0]["distance"], 2
                ),
                "end_snap_distance_m": round(
                    result["waypoints"][1]["distance"], 2
                )
            }

        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == 2:
                raise RuntimeError(
                    f"Gagal menghubungi OSRM: {error}"
                )

            print("Koneksi gagal. Mencoba kembali...")
            time.sleep(3)

    raise RuntimeError("Permintaan OSRM gagal.")


def create_direction(route, start_terminal, end_terminal, direction):
    print(
        f"  Mengambil jalur {direction}: "
        f"{start_terminal['stop_name']} -> "
        f"{end_terminal['stop_name']}"
    )

    result = request_osrm(start_terminal, end_terminal)

    return {
        "direction": direction,
        "from_terminal_id": start_terminal["stop_id"],
        "from_terminal_name": start_terminal["stop_name"],
        "to_terminal_id": end_terminal["stop_id"],
        "to_terminal_name": end_terminal["stop_name"],
        "distance_m": result["distance_m"],
        "duration_s": result["duration_s"],
        "geometry": result["geometry"],
        "start_snap_distance_m": result["start_snap_distance_m"],
        "end_snap_distance_m": result["end_snap_distance_m"]
    }


# ============================================================
# PROSES UTAMA
# ============================================================

def main():
    print("=" * 60)
    print("GENERATOR ROUTE PATHS - FLEET TELEMATICS")
    print("=" * 60)

    # Periksa keberadaan file
    if not STOPS_FILE.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {STOPS_FILE}")

    if not ROUTES_FILE.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {ROUTES_FILE}")

    # Baca master data
    stops_data = load_json(STOPS_FILE)
    routes_data = load_json(ROUTES_FILE)

    stops = {
        stop["stop_id"]: stop
        for stop in stops_data["stops"]
    }

    route_paths = []

    # Proses setiap koridor
    for route in routes_data["routes"]:
        route_id = route["route_id"]

        print(f"\nMemproses {route_id}: {route['route_name']}")

        start_id = route["start_terminal_id"]
        end_id = route["end_terminal_id"]

        if start_id not in stops or end_id not in stops:
            raise ValueError(
                f"Terminal tidak ditemukan pada koridor {route_id}"
            )

        start_terminal = stops[start_id]
        end_terminal = stops[end_id]

        # Jalur pergi
        outbound = create_direction(
            route,
            start_terminal,
            end_terminal,
            "outbound"
        )

        time.sleep(1)

        # Jalur pulang dihitung terpisah karena jalan satu arah
        return_path = create_direction(
            route,
            end_terminal,
            start_terminal,
            "return"
        )

        # Peringatan jika titik terminal terlalu jauh dari jalan terdekat
        for direction_data in (outbound, return_path):
            if (
                direction_data["start_snap_distance_m"] > 200
                or direction_data["end_snap_distance_m"] > 200
            ):
                print(
                    "  PERINGATAN: Titik terminal tersnap lebih dari "
                    "200 meter dari koordinat awal/akhir."
                )

        route_paths.append({
            "route_id": route_id,
            "route_name": route["route_name"],
            "outbound": outbound,
            "return": return_path
        })

        print(
            f"  Jarak pergi : {outbound['distance_m'] / 1000:.2f} km"
        )
        print(
            f"  Jarak pulang: {return_path['distance_m'] / 1000:.2f} km"
        )

        # Beri jeda sebelum permintaan koridor berikutnya
        time.sleep(1)

    # Bentuk file output
    output_data = {
        "metadata": {
            "project": "PID-C-05 Fleet Telematics",
            "source": "OpenStreetMap via OSRM Routing API",
            "profile": "driving",
            "geometry_type": "GeoJSON LineString",
            "coordinate_order": "[longitude, latitude]",
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "attribution": "© OpenStreetMap contributors",
            "total_routes": len(route_paths)
        },
        "route_paths": route_paths
    }

    # Simpan hanya setelah seluruh rute berhasil diperoleh
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print("GENERASI ROUTE PATHS BERHASIL")
    print("=" * 60)
    print(f"Jumlah koridor : {len(route_paths)}")
    print(f"Jumlah jalur   : {len(route_paths) * 2}")
    print(f"File output    : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nPROSES GAGAL:")
        print(error)
        print(
            "\nPeriksa koneksi internet, koordinat terminal, "
            "dan ketersediaan OSRM."
        )
