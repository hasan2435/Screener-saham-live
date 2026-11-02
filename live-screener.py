#!/usr/bin/env python3
"""
Live Screener Saham Gorengan - skrip mandiri untuk dijalankan sendiri.
Sumber data: Yahoo Finance publik IDX (chart 5 menit, gratis, tanpa API key).
Bukan feed langsung BEI dan bukan real-time per tick.
Cara jalan:  python3 live-screener.py
Butuh: Python 3 + internet saja (tidak perlu install library tambahan).
"""
import json, math, time, urllib.request

WATCHLIST = ["ASLI","FUTR","PTRO","VKTR","PGAS","GOTO","TPIA","CUAN","BRPT",
             "DSSA","BUMI","AADI","ENRG","INDY","MYOH","KINO","LINK","PTIS","SULI","NASI"]
# Saham Papan Akselerasi (ARA/ARB 10% simetris) - dari sumber publik InvestasiKu/Kontan/Stockbit/MediaSaham
# Papan bisa berubah lewat evaluasi BEI, cek ulang di aplikasi sekuritas
ACCELERATION = ["PACK","PPGL","CASH","CHIP","NANO","WIDI","IDEA","SMKM","RELF","MGLV","KING","KLIN","RUNS","FLMC","IBOS","PLAN","NAYZ","HAJJ","UDNG","FIMP","IPAC","EURO","LUCY","PGJO","AMMS"]  # UVCR DIHAPUS: bukti sekuritas terbaru menunjukkan UVCR reguler, ARA Senin 234 / ARB 162 dari close 174, bukan akselerasi 10%
# Kandidat multibagger gorengan low cap dari screening sebelumnya
# (harga live dicek, cap/fundamental adalah data screening terakhir - cek ulang sebelum beli)
MULTIBAGGER = [
    ("LABA", 99), ("RGAS", 89), ("DPNS", 103), ("IKAN", 49),
    ("SPRE", 47), ("TNCA", 58), ("RICY", None), ("CHEM", None),
]

def fetch(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.JK?range=1d&interval=5m"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    meta = res["meta"]
    q = res["indicators"]["quote"][0]
    pairs = [(c, v or 0) for c, v in zip(q["close"], q["volume"]) if c is not None]
    closes = [c for c, v in pairs]
    vols = [v for c, v in pairs]
    if not closes:
        return None
    price = closes[-1]
    prev = meta.get("chartPreviousClose") or closes[0]
    change = (price - prev) / prev * 100 if prev else 0
    # VWAP intraday: sum(close*volume)/sum(volume)
    tv = sum(c*v for c, v in zip(closes, vols))
    vv = sum(vols)
    vwap = tv / vv if vv else price
    low, high = min(closes), max(closes)
    avg_vol = sum(vols) / len(vols) if vols else 0
    vol_ratio = (vols[-3:] and sum(vols[-3:])/3/avg_vol) if avg_vol else 0
    return {"symbol": symbol, "price": price, "prev": prev, "change": change,
            "vwap": vwap, "low": low, "high": high, "vol_ratio": vol_ratio,
            "vol": vols[-1] if vols else 0}

def fraction(price):
    if price < 200: return 1
    if price <= 5000: return 5
    return 25

def ara_arb(prev, board="reguler"):
    # Papan Akselerasi: ARA/ARB 10% simetris di atas Rp10, Rp1 untuk Rp1-Rp10
    if board == "akselerasi":
        if prev <= 10:
            return prev + 1, prev - 1
        ara_pct, arb_pct = 10, 10
    elif prev <= 10: ara_pct, arb_pct = 0, 0
    elif prev <= 200: ara_pct, arb_pct = 35, 7
    elif prev <= 5000: ara_pct, arb_pct = 25, 7
    else: ara_pct, arb_pct = 20, 7
    ara = math.floor(prev * (1 + ara_pct/100) / fraction(prev)) * fraction(prev)
    arb = math.ceil(prev * (1 - arb_pct/100) / fraction(prev)) * fraction(prev)
    return ara, arb

def signals(s):
    out = []
    if s["price"] > s["vwap"] and s["change"] > 0: out.append("VWAP")
    if s["price"] > s["vwap"] and 2 <= s["change"] < 12 and s["vol_ratio"] > 2: out.append("AKUM+SCALPING")
    ara, _ = ara_arb(s["prev"], "akselerasi" if s["symbol"] in ACCELERATION else "reguler")
    dist = (ara - s["price"]) / s["price"] * 100 if s["price"] else 99
    if dist <= 10: out.append(f"ARA HUNTER (jarak {dist:.1f}%)")
    if 1 <= s["change"] <= 3 and s["price"] > s["vwap"] and s["vol_ratio"] > 2: out.append("SCALPING AWAL")
    if -3 <= s["change"] < 1 and s["price"] >= s["low"] * 1.02 and s["vol_ratio"] > 2: out.append("SCALPING AWAL (rebound)")
    return out

def load_all(symbols):
    rows = []
    for sym in symbols:
        try:
            s = fetch(sym)
            if s: rows.append(s)
        except Exception as e:
            print(f"  ! {sym} gagal: {e}")
        time.sleep(0.2)
    return rows

def menu_sinyal():
    rows = load_all(WATCHLIST)
    print("\n=== SINYAL AKTIF ===")
    for s in rows:
        sig = signals(s)
        if sig:
            print(f"{s['symbol']:6} Rp{s['price']:.0f} ({s['change']:+.2f}%) VWAP {s['vwap']:.0f} Vol {s['vol_ratio']:.1f}x  -> {', '.join(sig)}")
    if not any(signals(s) for s in rows):
        print("Tidak ada sinyal aktif saat ini.")
    print("\n=== SEMUA 20 SAHAM ===")
    for s in rows:
        print(f"{s['symbol']:6} Rp{s['price']:.0f} ({s['change']:+.2f}%)  VWAP {s['vwap']:.0f}  Low {s['low']:.0f} High {s['high']:.0f}")

def menu_ara():
    rows = load_all(WATCHLIST + [t for t in ACCELERATION if t not in WATCHLIST])
    print("\n=== ARA / ARB HUNTER ===")
    print("Reguler: ARA 35/25/20%, ARB 7% | Papan Akselerasi: ARA/ARB 10% simetris")
    for s in sorted(rows, key=lambda x: (ara_arb(x['prev'], "akselerasi" if x['symbol'] in ACCELERATION else "reguler")[0]-x['price'])/x['price']):
        board = "akselerasi" if s['symbol'] in ACCELERATION else "reguler"
        ara, arb = ara_arb(s['prev'], board)
        label = " [AKSELERASI 10%]" if board == "akselerasi" else ""
        print(f"{s['symbol']:6} Rp{s['price']:.0f}  ARA {ara:.0f} (+{(ara-s['price'])/s['price']*100:.1f}%)  ARB {arb:.0f}  prev {s['prev']:.0f}{label}")

def menu_volume():
    rows = load_all(WATCHLIST)
    print("\n=== TOP GAINER ===")
    for s in sorted(rows, key=lambda x: -x['change'])[:5]:
        print(f"{s['symbol']:6} Rp{s['price']:.0f} ({s['change']:+.2f}%) Vol {s['vol_ratio']:.1f}x")
    print("\n=== TOP LOSER ===")
    for s in sorted(rows, key=lambda x: x['change'])[:5]:
        print(f"{s['symbol']:6} Rp{s['price']:.0f} ({s['change']:+.2f}%) Vol {s['vol_ratio']:.1f}x")
    print("\n=== VOLUME BURST TERTINGGI ===")
    for s in sorted(rows, key=lambda x: -x['vol_ratio'])[:5]:
        print(f"{s['symbol']:6} Vol {s['vol_ratio']:.1f}x  Rp{s['price']:.0f} ({s['change']:+.2f}%)")

def menu_multibagger():
    rows = load_all([c[0] for c in MULTIBAGGER])
    print("\n=== CALON MULTIBAGGER - HANYA GORENGAN LOW CAP ===")
    print("Filter: harga <= Rp500. Cap target <= Rp100 M (data screening terakhir).")
    print("Ini screening data publik, BUKAN rekomendasi pasti / jaminan multibagger.")
    for s in rows:
        cap = dict(MULTIBAGGER).get(s['symbol'])
        cap_txt = f"Rp{cap} M" if cap else "cek ulang"
        lolos = "LOLOS" if s['price'] <= 500 else "TIDAK LOLOS (harga >500)"
        print(f"{s['symbol']:6} Rp{s['price']:.0f} ({s['change']:+.2f}%)  Cap {cap_txt}  -> {lolos}")

def main():
    print("Live Screener Saham Gorengan (Yahoo Finance IDX, 5 menit)")
    while True:
        print("\nMenu: 1=Sinyal Aktif  2=ARA/ARB Hunter  3=Volume/Gainer/Loser  4=Multibagger Low Cap  0=Keluar")
        p = input("Pilih: ").strip()
        if p == "0": break
        elif p == "1": menu_sinyal()
        elif p == "2": menu_ara()
        elif p == "3": menu_volume()
        elif p == "4": menu_multibagger()
        else: print("Pilihan tidak dikenal.")

if __name__ == "__main__":
    main()
