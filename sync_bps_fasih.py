import requests
import json
import os
import time

BASE_URL = "https://fasih-sm.bps.go.id/region/api/v1/region"

# Group ID yang Anda berikan
GROUP_ID = "a45adac1-e711-4c15-b3f9-1f30fc151565"

# Headers dengan Cookie terbaru Anda (Gres & Valid)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cookie": (
        "f5avraaaaaaaaaaaaaaaa_session_=JMIDELFCJMPOJIHPMLBFCAPPOBKMOOIFCHECHNKCOHCNPOEPHFAJKEPLPKICDMDDBIGDDAOBPGMNMBGOHGFAODJNFDJPOMCAHNHGGICOPCJCDAMGJIIPHCAJNGGIPCEM; "
        "f5avraaaaaaaaaaaaaaaa_session_=DHHIJPBFCHAMFBHCMJOKCLGJOEKMMEKEILNNKGGEPLGMONBBLCIMFMEAHFEDOBGELIMDNKNBCHLDCIDKFGBALIGFFDMLDEGDMJNOPAOLIOBOFLOGOGIGLLGIKAALJIKH; "
        "_ga=GA1.1.1314380881.1780642760; _ga_8D6M21ED9K=GS2.1.s1780642759$o1$g1$t1780642786$j33$l0$h0; "
        "XSRF-TOKEN=52dc2a6a-51a3-4a29-a3a8-ee7fe399ccef; db8ca2b43ed851cc93e71fd5fd72bff7=fcf7cbfcc6498dc2ca2d4ca85ca9ed9b; "
        "SESSION=207e4e47-bcdd-4568-95fc-17d715389fa3; TS01bafd94=01266d26d044eb0464a777599a35d9b6ff19a7450dfbbf08b5471430b84678e507d997479a3c2acca89ad0a77a3c1f57ef74df5722; "
        "f5avraaaaaaaaaaaaaaaa_session_=JCBIGAKKGIIBPCCCCPCPBFGEPILICJHOBNFJFJCCMICIELDEANOKDCBODCFFGIDHBFCDIPLEBHHEMMIBENJAMGENEDOIAIDIJMIPAJKOFNNFAICBOLPFAFANIMBOBANO; "
        "TSPD_101=0868f8be6fab2800c0ae68d50d6113dc74d9881b0e1d3ee98cc966171b5c2ea5db0f2a68625a848abcc5bf419c06bb160825372b3a0518009de6d6a131ae7c185ca1732140a3428bba23ce13beb1c95e; "
        "TS5220f739077=0868f8be6fab2000477fc63d4eddc6578222f75590572192e9647069ae882af2310e30b3c34cc1c92d9bd216c6ca918f08649752b2172000fc8826fe51ff92dcf59b01bf04a08c89ce41d67087b912eab9e0bf9ce79b1b83; "
        "TS5220f739029=0868f8be6fab28001695bf47915509343fb2497a1f7102e1a2ffb4a8b0533a997ed66c2297360701511a70122ba06223; "
        "TSf1edb2d2027=0868f8be6fab200054ce40160c201151e3c5455239c623e8fa4713bddeddcaecc9eec0f152af0cb408fcb94fa51130002f89d85097fea2385763f852ee3a7a8315e0c4d117a5b4bbe4a0ef941d25e560e85849f35312b155468fb41328905998"
    )
}

def fetch_data(endpoint, params):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"⚠️ Server BPS merespon dengan Status Code: {response.status_code} pada [{endpoint}]")
        return None
    except Exception as e:
        print(f"❌ Koneksi gagal pada [{endpoint}]: {e}")
        return None

def main():
    print("🚀 Memulai penarikan DATA ASLI bertingkat dari Web Fasih BPS...")
    provinsi_key = "Provinsi Sulawesi Selatan"
    kota_key = "Kota Makassar"
    
    output_data = {provinsi_key: {kota_key: {}}}
    
    # 1. Ambil data level 3 (Kecamatan)
    data_kecamatan = fetch_data("level3", {"groupId": GROUP_ID})
    
    if not data_kecamatan or "data" not in data_kecamatan:
        print("❌ Gagal mengambil data Kecamatan. Kemungkinan Cookie kedaluwarsa atau Group ID salah.")
        raise ValueError("Proses dihentikan: Autentikasi API Fasih BPS Gagal.")

    list_kecamatan = data_kecamatan.get("data", [])
    print(f"✔ Berhasil memuat {len(list_kecamatan)} Kecamatan di {kota_key}.")

    # 2. Iterasi setiap Kecamatan untuk mencari Kelurahan (level 4)
    for idx, kec in enumerate(list_kecamatan, start=1):
        kec_id = kec.get("id")
        kec_name = kec.get("name")
        print(f"[{idx}/{len(list_kecamatan)}] -> Memproses {kec_name}...")
        
        output_data[provinsi_key][kota_key][kec_name] = {}
        
        # Ambil data level 4 (Kelurahan) berdasarkan ID Kecamatan
        data_kelurahan = fetch_data("level4", {"groupId": GROUP_ID, "level3Id": kec_id})
        if not data_kelurahan or "data" not in data_kelurahan:
            print(f"   ⚠️ Melewati {kec_name} (Kelurahan gagal dimuat)")
            continue
            
        # 3. Iterasi setiap Kelurahan untuk mencari SLS (level 5)
        for kel in data_kelurahan.get("data", []):
            kel_id = kel.get("id")
            kel_name = kel.get("name")
            
            output_data[provinsi_key][kota_key][kec_name][kel_name] = {
                "id_kelurahan": kel_id,
                "SLS": []
            }
            
            # Ambil data level 5 (SLS / RT-RW) berdasarkan ID Kelurahan
            data_sls = fetch_data("level5", {"groupId": GROUP_ID, "level4Id": kel_id})
            if data_sls and "data" in data_sls:
                for sls in data_sls.get("data", []):
                    output_data[provinsi_key][kota_key][kec_name][kel_name]["SLS"].append({
                        "id_sls": sls.get("id"),
                        "nama_sls": sls.get("name")
                    })
            
            # Jeda aman bertahap (0.4 detik) agar tidak dicurigai sebagai serangan DDOS oleh server BPS
            time.sleep(0.4)

    # 4. Amankan dan Simpan Hasil Akhir ke Repositori
    folder_output = "data_output"
    os.makedirs(folder_output, exist_ok=True)
    
    file_path = f"{folder_output}/struktur_wilayah_sulsel.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        
    print(f"🎉 Selesai! Data asli berhasil disimpan di: {file_path}")

if __name__ == "__main__":
    main()
