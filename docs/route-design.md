# Dokumentasi Perancangan Rute Bus Kota
## Proyek Pemrosesan dan Infrastruktur Data – PID-C-05

## 1. Pendahuluan

Dokumen ini menjelaskan perancangan rute, terminal, jadwal operasional, dan jalur perjalanan bus yang digunakan dalam proyek Fleet Telematics dengan studi kasus simulasi bus kota di wilayah Malang.

Perancangan ini bertujuan menyediakan konfigurasi perjalanan yang konsisten untuk mendukung simulasi pergerakan bus, pemantauan posisi GPS, pengolahan data streaming, pencatatan aktivitas terminal, serta visualisasi pada dashboard.

Koridor yang dirancang merupakan koridor simulasi untuk kebutuhan proyek, bukan representasi resmi trayek bus kota yang beroperasi di Malang.

## 2. Ruang Lingkup Perancangan

Perancangan rute mencakup:

1. Empat koridor perjalanan simulasi.
2. Lima terminal sebagai titik awal dan akhir perjalanan.
3. Dua puluh bus yang dibagi ke dalam empat koridor.
4. Jadwal keberangkatan dan waktu berhenti di terminal.
5. Jalur perjalanan outbound dan return.
6. Konfigurasi geofence terminal untuk mendeteksi aktivitas kedatangan dan keberangkatan bus.

Sistem dirancang untuk beroperasi pada rentang waktu pukul 05.00–23.00.

## 3. Perancangan Koridor

Terdapat empat koridor simulasi yang dirancang berdasarkan hubungan geografis antarterminal di wilayah Malang.

| ID Koridor | Nama Koridor | Terminal Awal | Terminal Akhir |
|---|---|---|---|
| R-01 | Utara–Selatan | Terminal Arjosari | Terminal Hamid Rusdi |
| R-02 | Utara–Barat | Terminal Arjosari | Terminal Landungsari |
| R-03 | Barat–Selatan | Terminal Landungsari | Terminal Hamid Rusdi |
| R-04 | Barat Daya–Timur | Terminal Mulyorejo | Terminal Madyopuro |

Setiap koridor memiliki lima bus sehingga keseluruhan sistem menggunakan 20 bus simulasi.

## 4. Data Terminal

Lima terminal digunakan sebagai titik awal dan akhir perjalanan.

| ID Terminal | Nama Terminal | Latitude | Longitude |
|---|---|---:|---:|
| T-01 | Terminal Arjosari | -7.935205 | 112.658384 |
| T-02 | Terminal Hamid Rusdi | -8.025997 | 112.643855 |
| T-03 | Terminal Landungsari | -7.925197 | 112.598150 |
| T-04 | Terminal Mulyorejo | -7.990433 | 112.599462 |
| T-05 | Terminal Madyopuro | -7.974556 | 112.670631 |

Koordinat terminal menggunakan titik lokasi yang telah dikumpulkan dari OpenStreetMap.

Setiap terminal memiliki konfigurasi geofence dengan radius 50 meter. Geofence digunakan untuk menentukan apakah posisi bus berada di sekitar area terminal.

## 5. Perancangan Armada dan Jadwal

Jumlah armada yang digunakan adalah 20 bus dengan pembagian sebagai berikut:

| Koridor | Jumlah Bus | Identitas Bus |
|---|---:|---|
| R-01 | 5 | BUS-R01-01 sampai BUS-R01-05 |
| R-02 | 5 | BUS-R02-01 sampai BUS-R02-05 |
| R-03 | 5 | BUS-R03-01 sampai BUS-R03-05 |
| R-04 | 5 | BUS-R04-01 sampai BUS-R04-05 |
| **Total** | **20** | |

Ketentuan jadwal operasional:

- Jam operasional: 05.00–23.00.
- Keberangkatan awal dimulai pukul 05.00.
- Jadwal keberangkatan awal setiap bus dibuat dengan interval 15 menit.
- Waktu berhenti atau dwell time di terminal direncanakan selama 10 menit.
- Perjalanan dirancang mendukung arah outbound dan return.

Jadwal lengkap masing-masing bus disimpan dalam file `data/routes/schedules.json`.

## 6. Perancangan Jalur Perjalanan

Jalur perjalanan dibuat menggunakan layanan OSRM dengan data jaringan jalan OpenStreetMap dan profil perjalanan driving.

Setiap koridor memiliki dua jalur:

- Outbound: perjalanan dari terminal awal menuju terminal akhir.
- Return: perjalanan dari terminal akhir menuju terminal awal.

Hasil pembuatan jalur:

| Koridor | Outbound | Return |
|---|---:|---:|
| R-01 | 12,98 km | 13,84 km |
| R-02 | 9,48 km | 9,50 km |
| R-03 | 15,11 km | 16,01 km |
| R-04 | 11,42 km | 11,64 km |

Secara keseluruhan terdapat delapan jalur perjalanan dengan total 3.907 titik koordinat.

Data jalur disimpan dalam format GeoJSON LineString pada file `data/routes/route_paths.json`.

Urutan koordinat GeoJSON yang digunakan adalah longitude kemudian latitude.

Jalur hasil OSRM merupakan jalur berbasis jaringan jalan untuk simulasi. Jalur tersebut tidak secara otomatis menjamin kesesuaian dengan aturan operasional atau pembatasan kendaraan bus di setiap ruas jalan.

## 7. Mekanisme Geofence Terminal

Sistem menggunakan geofence dengan radius 50 meter pada setiap terminal.

Mekanisme yang direncanakan:

1. Sistem menerima posisi GPS bus.
2. Posisi bus dibandingkan dengan koordinat terminal.
3. Jika bus memasuki radius geofence, sistem dapat mencatat indikasi kedatangan.
4. Jika bus meninggalkan area terminal, sistem dapat mencatat indikasi keberangkatan.
5. Waktu kedatangan dan keberangkatan digunakan untuk analisis aktivitas terminal dan keterlambatan.

Untuk mengurangi perubahan status akibat variasi pembacaan GPS, konfigurasi keberangkatan menggunakan jarak 60 meter dari titik terminal sebagai ambang keluar area.

Aturan pendeteksian dan pencatatan event perlu diterapkan secara konsisten pada simulator dan pemrosesan streaming.

## 8. Perubahan Desain: Geofence Berbasis Terminal

Pada rancangan awal, pemantauan geofence direncanakan mencakup halte perantara di sepanjang koridor.

Namun, dalam pengembangan rancangan, pemantauan geofence difokuskan pada terminal karena keterbatasan data lokasi halte perantara yang dapat diverifikasi.

Dengan perubahan ini:

- Pencatatan kedatangan dan keberangkatan difokuskan pada terminal.
- Analisis keterlambatan menggunakan jadwal dan aktivitas terminal.
- Tidak dilakukan pencatatan kedatangan pada halte perantara.
- Pemantauan penyimpangan jalur tetap menggunakan geometri rute perjalanan.

Perubahan ini merupakan penyesuaian ruang lingkup desain dan perlu diselaraskan dengan ketentuan tugas serta persetujuan pengajar.

## 9. Struktur File Konfigurasi

Seluruh konfigurasi perancangan rute disimpan pada direktori `data/routes/`.

| File | Fungsi |
|---|---|
| `routes.json` | Menyimpan informasi empat koridor dan terminal awal-akhir. |
| `stops.json` | Menyimpan data lima terminal, koordinat, dan konfigurasi geofence. |
| `schedules.json` | Menyimpan jadwal operasional 20 bus. |
| `route_paths.json` | Menyimpan geometri jalur outbound dan return. |

File-file tersebut menjadi sumber konfigurasi bersama agar simulator, database, streaming, dan dashboard menggunakan identitas rute serta terminal yang konsisten.

## 10. Hasil Validasi

Validasi dilakukan terhadap konfigurasi koridor, terminal, jadwal, dan geometri jalur.

Hasil validasi:

| Parameter | Hasil |
|---|---:|
| Jumlah koridor | 4 |
| Jumlah terminal | 5 |
| Jumlah jadwal bus | 20 |
| Jumlah ID bus unik | 20 |
| Jumlah bus per koridor | 5 |
| Jumlah jalur perjalanan | 8 |
| Jumlah titik koordinat | 3.907 |
| Referensi terminal tidak valid | 0 |
| Referensi jadwal tidak valid | 0 |
| Geometri jalur tidak valid | 0 |
| Jalur dengan jarak snapping di atas 200 meter | 0 |

Hasil tersebut menunjukkan bahwa konfigurasi rute dan struktur geometri jalur telah berhasil dibuat serta lolos pemeriksaan yang dilakukan.

Validasi ini belum membuktikan bahwa seluruh jalur sesuai dengan kondisi lalu lintas aktual atau pembatasan kendaraan di lapangan.

## 11. Kesimpulan

Perancangan rute Fleet Telematics telah menghasilkan empat koridor simulasi, lima terminal, 20 konfigurasi jadwal bus, dan delapan jalur perjalanan.

Seluruh konfigurasi telah disimpan dalam file JSON agar dapat digunakan bersama oleh anggota kelompok yang bertanggung jawab pada simulator, streaming, database, ETL, dan dashboard.

Dengan adanya konfigurasi terpusat, setiap komponen sistem diharapkan menggunakan identitas bus, koridor, terminal, dan jadwal yang konsisten.