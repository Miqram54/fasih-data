import requests
import json
import os
import time

# Konfigurasi Utama API BPS Fasih
BASE_URL = "https://fasih-sm.bps.go.id/region/api/v1/region"
GROUP_ID = "a45adac1-e711-4c15-b3f9-1f30fc151565" 

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    # TEMPELKAN COOKIE SEGAR ANDA DI BAWAH INI SEBAGAI PENGGANTI
    "Cookie": "f5avraaaaaaaaaaaaaaaa_session_=JJOMIHGIKNJLCFBINIPNPGLGMGGODFFOAGBAEBDGMHHLDHLAJPHOGLKPIOBGMLKLNAADANCBLJDBOLHOCOGADLAKLBDBHLHHIGEEEBEOEPABFCJPMFGIPGLINLJJKDPD; f5avraaaaaaaaaaaaaaaa_session_=OIJEHJHAMPMJKNANPMCECKEMLGJLLCGIPBJFOGOPODLOINFJPJELCNHBNLEPJEEBLOCDBDIKNEHPLNKNLLKAFMFPBBAAKKLABBGHHBKMPOKCFFDDOOBCEBMJKKEBOCAN; _ga=GA1.1.1314380881.1780642760; _ga_8D6M21ED9K=GS2.1.s1780642759$o1$g1$t1780642786$j33$l0$h0; XSRF-TOKEN=52dc2a6a-51a3-4a29-a3a8-ee7fe399ccef; db8ca2b43ed851cc93e71fd5fd72bff7=fcf7cbfcc6498dc2ca2d4ca85ca9ed9b; SESSION=207e4e47-bcdd-4568-95fc-17d715389fa3; f5avraaaaaaaaaaaaaaaa_session_=MILOHJNMGDPPABPMICJHDBKKDDJEJOLBBKELPONDDMGHKEMJBMMKJAKDADEIDGGHMJODMBOIBEJDFAMLIOKAHFGDBBFCBPPOBEFIBBKEBBPDPINKICKNJIPELFNDFKBG; TS01bafd94=01266d26d0c05ddec49105d676dd1d6bcc73c8b82c948fb0e71c0878064bc85c4a97551e535a482246ac2b9e0f8bff23fe66fda671; TSf1edb2d2027=0868f8be6fab2000d3d777f608b9c24ed6f2d20ee0f4ed913db8cce73f4278a90bdd2cabce4a4b6d084d8de2a41130000b51ff7ed7ab6c2090506c11d7d176b297e1132992eec274d2a2f24200b285d4b6a0d61a2e2779827b688791f6eca254"
}

def fetch_data(endpoint, params):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code in [401, 403]:
            print(f"⚠️ Akses ditolak (Status {response.status_code}). Cookie kedaluwarsa.")
            return None
        return None
    except Exception as e:
        print(f"Error request {endpoint}: {e}")
        return None

def main():
    print("Memulai penarikan data wilayah terstruktur...")
    
    provinsi_key = "Provinsi Sulawesi Selatan"
    kota_key = "Kota Makassar"
    
    output_data = {
        provinsi_key: {
            kota_key: {}
        }
    }
    
    # 1. Ambil data level 3 (Kecamatan)
    params_l3 = {"groupId": GROUP_ID}
    data_kecamatan = fetch_data("level3", params_l3)
    
    if not data_kecamatan or "data" not in data_kecamatan:
        print("Gagal mengambil data Kecamatan. Periksa apakah Cookie Anda sudah diganti dengan yang baru.")
        return

    # 2. Iterasi setiap Kecamatan
    for kec in data_kecamatan.get("data", []):
        kec_id = kec.get("id")
        kec_name = kec.get("name")
        print(f"-> Memproses Kecamatan: {kec_name}")
        
        output_data[provinsi_key][kota_key][kec_name] = {}
        
        # 3. Ambil data level 4 (Kelurahan) berdasarkan ID Kecamatan
        params_l4 = {"groupId": GROUP_ID, "level3Id": kec_id}
        data_kelurahan = fetch_data("level4", params_l4)
        
        if not data_kelurahan or "data" not in data_kelurahan:
            continue
            
        for kel in data_kelurahan.get("data", []):
            kel_id = kel.get("id")
            kel_name = kel.get("name")
            print(f"   --> Kelurahan: {kel_name}")
            
            output_data[provinsi_key][kota_key][kec_name][kel_name] = {
                "id_kelurahan": kel_id,
                "SLS": []
            }
            
            # 4. Ambil data level 5 (SLS / RT-RW) berdasarkan ID Kelurahan
            params_l5 = {"groupId": GROUP_ID, "level4Id": kel_id}
            data_sls = fetch_data("level5", params_l5)
            
            if data_sls and "data" in data_sls:
                for sls in data_sls.get("data", []):
                    output_data[provinsi_key][kota_key][kec_name][kel_name]["SLS"].append({
                        "id_sls": sls.get("id"),
                        "nama_sls": sls.get("name")
                    })
            
            # Jeda aman agar server BPS tidak overload
            time.sleep(0.6)

    # 5. Simpan Hasil Akhir ke Repositori
    os.makedirs("data_output", exist_ok=True)
    with open("data_output/struktur_wilayah_sulsel.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        
    print("🎉 Selesai! Data disimpan di data_output/struktur_wilayah_sulsel.json")

if __name__ == "__main__":
    main()
