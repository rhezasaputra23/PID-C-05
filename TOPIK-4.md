# Topik 4 — Fleet Telematics

Operator armada ingin memantau posisi dan kondisi kendaraan secara real-time, mendeteksi perilaku berisiko, dan menganalisis kinerja operasional dari data historis.

## Varian A — Bus Kota

Armada bus kota yang melayani beberapa rute tetap dengan halte terjadwal.

| Perangkat | Jumlah min. | Field | Rentang normal |
|---|---|---|---|
| GPS tracker bus | 20 | `lat`, `lon`, `speed_kmh`, `heading` | 0–60 km/jam |
| Penghitung penumpang | 20 (menyatu dengan bus) | `passengers_in`, `passengers_out`, `occupancy` | 0–80 orang |

Rute dan halte (koordinat, urutan, jadwal) disimpan di MySQL. Simulator menggerakkan bus di sepanjang rute dengan kecepatan bervariasi dan kemacetan acak.

**Tantangan signature — Geofencing dan deteksi keterlambatan halte**
- Geofence radius (mis. 50 m) di setiap halte: catat *event* tiba dan berangkat dengan rumus jarak Haversine.
- Bandingkan waktu tiba dengan jadwal: alert bila terlambat > 5 menit.
- Deteksi bus keluar dari koridor rute (jarak ke rute > 200 m).

## Varian B — Truk Logistik

Armada truk logistik antarkota dengan data GPS, bahan bakar, dan mesin.

| Perangkat | Jumlah min. | Field | Rentang normal |
|---|---|---|---|
| GPS tracker | 20 | `lat`, `lon`, `speed_kmh` | 0–90 km/jam |
| Sensor bahan bakar | 20 (menyatu) | `fuel_l`, `fuel_pct` | tangki 200–400 L |
| Data mesin (CAN-bus) | 20 (menyatu) | `engine_temp_c`, `rpm`, `accel_ms2` | 80–100 °C |

**Tantangan signature — Skor perilaku pengemudi dan deteksi penurunan BBM**
- Event *harsh braking* (`accel_ms2` < −3.5), *harsh acceleration* (> 3), dan *overspeed* (> 90 km/jam).
- Skor pengemudi harian 0–100 = 100 − penalti per event per 100 km.
- Alert dugaan pencurian BBM: `fuel_l` turun > 10 % dalam window 5 menit saat kendaraan berhenti.

## Contoh Skema Pesan

```json
{
  "device_id": "TRK-014",
  "device_type": "telematics",
  "vehicle_id": "B 9123 KX",
  "timestamp": "2026-11-20T09:15:02Z",
  "data": { "lat": -6.9147, "lon": 107.6098, "speed_kmh": 54.2, "fuel_l": 212.5, "engine_temp_c": 91.0 }
}
```

Field `device_id`, `device_type`, `vehicle_id`, `timestamp`, dan `data` wajib ada.

## Data Kotor yang Disarankan

- *GPS jump*: koordinat melompat jauh dalam 1 detik (kecepatan implisit tidak mungkin).
- Koordinat `0,0` atau `null` saat sinyal hilang.
- Pesan terlambat atau tidak berurutan setelah kendaraan keluar dari area tanpa sinyal (*store-and-forward*).
- Pesan duplikat.

## KPI Streaming dan Alert

- Window 1 dan 15 menit: kecepatan rata-rata, jumlah kendaraan bergerak/berhenti.
- Peta posisi kendaraan terkini di dashboard.
- Varian A: ketepatan waktu per rute. Varian B: konsumsi BBM (km/L) per truk.

## Saran Star Schema

- **Fakta**: `fact_trip` (per perjalanan), `fact_stop_event` atau `fact_driving_event`, `fact_alert`.
- **Dimensi**: `dim_vehicle`, `dim_route`/`dim_stop` (Varian A) atau `dim_driver` (Varian B), `dim_time`, `dim_location`.

## Kriteria Penerimaan

1. Minimal 20 kendaraan bergerak di koordinat realistis (jalan atau rute nyata di satu kota/wilayah) dan tampil di peta dashboard.
2. Event signature (tiba/terlambat atau harsh event/BBM turun) terdeteksi secara streaming dan tercatat di warehouse.
3. Warehouse dapat menjawab: rute/pengemudi terbaik dan terburuk selama 7 hari beserta metriknya.
4. GPS jump dan pesan tidak berurutan ditangani (dibuang atau dikoreksi) dan jumlahnya dilaporkan.
