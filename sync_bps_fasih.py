import requests
import json
import os
import time

BASE_URL = "https://fasih-sm.bps.go.id/region/api/v1/region"
GROUP_ID = "a45adac1-e711-4c15-b3f9-1f30fc151565"

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
        "TS5220f739029=0868f8be6fab28004cce8dcb9023f176ae99bbf6a039107660bef6d217805b8724e21e1a2c637dd93167101ae55ea0e6; "
        "TSf1edb2d2027=0868f8be6fab200041ec38ebd195925b21ed107cc0bc381fdb1997557bfcadc36c563159c4bdc83608ecec0532113000b57928071a2fef345763f852ee3a7a8315e0c4d117a5b4bbe4a0ef941d25e560e85849f35312b155468fb41328905998"
    )
}

def fetch_data(endpoint, params):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"❌ Server BPS menolak request [{endpoint}]. Status Code: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Terjadi masalah koneksi pada [{endpoint}]: {e}")
        return None

def main():
    print("Memulai sinkronisasi struktur wilayah...")
    provinsi_key = "Provinsi Sulawesi Selatan"
    kota_key = "Kota Makassar"
    
    output_data = {provinsi_key: {kota_key: {}}}
    
    data_kecamatan = fetch_data("level3", {"groupId": GROUP_ID})
    
    if not data_kecamatan or "data" not in data_kecamatan:
        print("❌ Gagal total mendapatkan data tingkat Kecamatan. Sesi cookie dipastikan sudah kedaluwarsa.")
        raise ValueError("Proses terhenti karena kegagalan autentikasi cookie API.")

    print(f"✔ Berhasil memuat {len(data_kecamatan['data'])} Kecamatan.")

    for kec in data_kecamatan.get("data", []):
        kec_id = kec.get("id")
        kec_name = kec.get("name")
        print(f"-> Memproses {kec_name}")
        
        output_data[provinsi_key][kota_key][kec_name] = {}
        data_kelurahan = fetch_data("level4", {"groupId": GROUP_ID, "level3Id": kec_id})
        
        if not data_kelurahan or "data" not in data_kelurahan:
            continue
            
        for kel in data_kelurahan.get("data", []):
            kel_id = kel.get("id")
            kel_name = kel.get("name")
            
            output_data[provinsi_key][kota_key][kec_name][kel_name] = {
                "id_kelurahan": kel_id,
                "SLS": []
            }
            
            data_sls = fetch_data("level5", {"groupId": GROUP_ID, "level4Id": kel_id})
            if data_sls and "data" in data_sls:
                for sls in data_sls.get("data", []):
                    output_data[provinsi_key][kota_key][kec_name][kel_name]["SLS"].append({
                        "id_sls": sls.get("id"),
                        "nama_sls": sls.get("name")
                    })
            time.sleep(0.5)

    os.makedirs("data_output", exist_ok=True)
    with open("data_output/struktur_wilayah_sulsel.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print("🎉 Pembaruan pohon data selesai tanpa hambatan!")

if __name__ == "__main__":
    main()
