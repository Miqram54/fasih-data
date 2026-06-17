import requests
import json
import os
import time

def main():
    print("🤖 Memulai sinkronisasi menggunakan DATA SIMULASI Struktur Makassar...")
    
    # Membuat tiruan struktur data persis seperti yang Anda inginkan
    provinsi_key = "Provinsi Sulawesi Selatan"
    kota_key = "Kota Makassar"
    
    print(f"-> Menyusun pohon data untuk {provinsi_key} -> {kota_key}...")
    
    # Ini adalah data simulasi lengkap beberapa kecamatan & kelurahan di Makassar
    simulasi_data = {
        provinsi_key: {
            kota_key: {
                "Kecamatan Rappocini": {
                    "Kelurahan Banta-Bantaeng": {
                        "id_kelurahan": "simulasi-l4-rappocini-banta",
                        "SLS": [
                            {"id_sls": "sls-001", "nama_sls": "RT 001 / RW 001"},
                            {"id_sls": "sls-002", "nama_sls": "RT 002 / RW 001"},
                            {"id_sls": "sls-003", "nama_sls": "RT 003 / RW 002"}
                        ]
                    },
                    "Kelurahan Ballaparang": {
                        "id_kelurahan": "simulasi-l4-rappocini-balla",
                        "SLS": [
                            {"id_sls": "sls-004", "nama_sls": "RT 001 / RW 001"},
                            {"id_sls": "sls-005", "nama_sls": "RT 002 / RW 001"}
                        ]
                    }
                },
                "Kecamatan Tamalate": {
                    "Kelurahan Parang Tambung": {
                        "id_kelurahan": "simulasi-l4-tamalate-parang",
                        "SLS": [
                            {"id_sls": "sls-006", "nama_sls": "RT 001 / RW 003"},
                            {"id_sls": "sls-007", "nama_sls": "RT 002 / RW 003"}
                        ]
                    },
                    "Kelurahan Jongaya": {
                        "id_kelurahan": "simulasi-l4-tamalate-jongaya",
                        "SLS": [
                            {"id_sls": "sls-008", "nama_sls": "RT 001 / RW 001"}
                        ]
                    }
                },
                "Kecamatan Panakkukang": {
                    "Kelurahan Masale": {
                        "id_kelurahan": "simulasi-l4-panakkukang-masale",
                        "SLS": [
                            {"id_sls": "sls-009", "nama_sls": "RT 001 / RW 004"},
                            {"id_sls": "sls-010", "nama_sls": "RT 002 / RW 004"}
                        ]
                    }
                }
            }
        }
    }
    
    print("✔ Struktur simulasi berhasil dibuat di memori komputer robot.")
    
    # Membuat folder output di dalam repositori GitHub
    folder_name = "data_output"
    file_name = f"{folder_name}/struktur_wilayah_sulsel.json"
    
    os.makedirs(folder_name, exist_ok=True)
    
    # Menyimpan menjadi file asli json
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(simulasi_data, f, indent=4, ensure_ascii=False)
        
    print(f"✔ File tiruan sukses ditulis di: {file_name}")
    print("🎉 Selesai! Menyerahkan file ke robot GitHub untuk proses upload balik.")

if __name__ == "__main__":
    main()
