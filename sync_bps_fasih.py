import requests
import json
import os
import time
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Konfigurasi Utama API BPS Fasih
BASE_URL = "https://fasih-sm.bps.go.id/region/api/v1/region"
GROUP_ID = "a45adac1-e711-4c15-b3f9-1f30fc151565" 
MAX_RETRIES = 3
RETRY_DELAY = 2  # detik

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    # TEMPELKAN COOKIE SEGAR ANDA DI BAWAH INI SEBAGAI PENGGANTI
    "Cookie": "f5avraaaaaaaaaaaaaaaa_session_=FCOCGAPNMPONFLNPGFHHKADBJFBMDMMDAKBLFNGGAHHMLGBIDOMNENFGMMCENHHFOKODKAGFHENEPHJDIFHAIFIECDADFHEEGIBBKODEFEAIJMBLHNIHIJNCGLOBGGJC; f5avraaaaaaaaaaaaaaaa_session_=OIJEHJHAMPMJKNANPMCECKEMLGJLLCGIPBJFOGOPODLOINFJPJELCNHBNLEPJEEBLOCDBDIKNEHPLNKNLLKAFMFPBBAAKKLABBGHHBKMPOKCFFDDOOBCEBMJKKEBOCAN; _ga=GA1.1.1314380881.1780642760; _ga_8D6M21ED9K=GS2.1.s1780642759$o1$g1$t1780642786$j33$l0$h0; XSRF-TOKEN=52dc2a6a-51a3-4a29-a3a8-ee7fe399ccef; db8ca2b43ed851cc93e71fd5fd72bff7=fcf7cbfcc6498dc2ca2d4ca85ca9ed9b; SESSION=207e4e47-bcdd-4568-95fc-17d715389fa3; f5avraaaaaaaaaaaaaaaa_session_=MILOHJNMGDPPABPMICJHDBKKDDJEJOLBBKELPONDDMGHKEMJBMMKJAKDADEIDGGHMJODMBOIBEJDFAMLIOKAHFGDBBFCBPPOBEFIBBKEBBPDPINKICKNJIPELFNDFKBG; TS01bafd94=01266d26d07a467ffa1d4167d94eb6d4f62207fe7aacc5b30a3a7331145ee2dd8321223b62df4050b947df93f8870d693a0b0bc9b3; TS5220f739029=0868f8be6fab2800c7032d4517ddf47ec28b942307ee70804c91c728d59ba7303da6f8aa5cbb56a45d2084a17065602b; TSf1edb2d2027=0868f8be6fab20007b015206c45fb0a78b02c0e521e43927a0e1d96301cfd061e901be5eb223a5810839e0e41a113000a9b07d33679da1b8d5a6d998208371a2b6531200be0e0826d67c1163bc394bba631edc5677b5c9231f8ce7a5bb0ceafc"
}

def create_session_with_retries():
    """Buat session dengan retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_data(endpoint, params, attempt=1):
    """Fetch data dengan retry logic"""
    try:
        session = create_session_with_retries()
        response = session.get(
            f"{BASE_URL}/{endpoint}",
            headers=HEADERS,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code in [401, 403]:
            print(f"⚠️ Akses ditolak (Status {response.status_code}). Cookie kedaluwarsa.")
            return None
        else:
            print(f"⚠️ Status {response.status_code} untuk endpoint {endpoint}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout pada endpoint {endpoint} (Attempt {attempt}/{MAX_RETRIES})")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return fetch_data(endpoint, params, attempt + 1)
        return None
        
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Connection Error pada {endpoint}: {str(e)[:100]} (Attempt {attempt}/{MAX_RETRIES})")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return fetch_data(endpoint, params, attempt + 1)
        return None
        
    except Exception as e:
        print(f"❌ Error request {endpoint}: {str(e)[:100]}")
        return None

def main():
    try:
        print("🚀 Memulai penarikan data wilayah terstruktur...")
        
        provinsi_key = "Provinsi Sulawesi Selatan"
        kota_key = "Kota Makassar"
        
        output_data = {
            provinsi_key: {
                kota_key: {}
            }
        }
        
        # 1. Ambil data level 3 (Kecamatan)
        print("📍 Mengambil data Kecamatan...")
        params_l3 = {"groupId": GROUP_ID}
        data_kecamatan = fetch_data("level3", params_l3)
        
        if not data_kecamatan or "data" not in data_kecamatan:
            print("❌ Gagal mengambil data Kecamatan. Periksa apakah Cookie Anda sudah diganti dengan yang baru.")
            sys.exit(1)

        total_kecamatan = len(data_kecamatan.get("data", []))
        print(f"✅ Berhasil mengambil {total_kecamatan} Kecamatan")

        # 2. Iterasi setiap Kecamatan
        for idx, kec in enumerate(data_kecamatan.get("data", []), 1):
            kec_id = kec.get("id")
            kec_name = kec.get("name")
            print(f"\n→ [{idx}/{total_kecamatan}] Memproses Kecamatan: {kec_name}")
            
            output_data[provinsi_key][kota_key][kec_name] = {}
            
            # 3. Ambil data level 4 (Kelurahan) berdasarkan ID Kecamatan
            params_l4 = {"groupId": GROUP_ID, "level3Id": kec_id}
            data_kelurahan = fetch_data("level4", params_l4)
            
            if not data_kelurahan or "data" not in data_kelurahan:
                print(f"   ⚠️ Tidak ada data Kelurahan untuk {kec_name}")
                continue
            
            total_kelurahan = len(data_kelurahan.get("data", []))
            print(f"   📌 Ditemukan {total_kelurahan} Kelurahan")
                
            for kel_idx, kel in enumerate(data_kelurahan.get("data", []), 1):
                kel_id = kel.get("id")
                kel_name = kel.get("name")
                print(f"      {kel_idx}. {kel_name}")
                
                output_data[provinsi_key][kota_key][kec_name][kel_name] = {
                    "id_kelurahan": kel_id,
                    "SLS": []
                }
                
                # 4. Ambil data level 5 (SLS / RT-RW) berdasarkan ID Kelurahan
                params_l5 = {"groupId": GROUP_ID, "level4Id": kel_id}
                data_sls = fetch_data("level5", params_l5)
                
                if data_sls and "data" in data_sls:
                    sls_count = len(data_sls.get("data", []))
                    for sls in data_sls.get("data", []):
                        output_data[provinsi_key][kota_key][kec_name][kel_name]["SLS"].append({
                            "id_sls": sls.get("id"),
                            "nama_sls": sls.get("name")
                        })
                
                # Jeda aman agar server BPS tidak overload
                time.sleep(0.6)

        # 5. Simpan Hasil Akhir ke Repositori
        os.makedirs("data_output", exist_ok=True)
        output_file = "data_output/struktur_wilayah_sulsel.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"\n✅ Selesai! Data disimpan di {output_file}")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error tidak terduga: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
