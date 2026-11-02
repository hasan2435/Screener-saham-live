# Screener Saham Live

Aplikasi web screener saham gorengan Indonesia (aplikasi web), plus skrip mandiri di repo ini.

## Isi repo
- `live-screener.py` — skrip Python 3 mandiri, tanpa library tambahan, memakai API chart publik Yahoo Finance IDX.
  - Menu: 1 = Sinyal Aktif, 2 = ARA/ARB Hunter, 3 = Volume/Gainer/Loser, 4 = Multibagger Low Cap, 0 = Keluar
  - Universe: 20 saham gorengan (ASLI, FUTR, PTRO, VKTR, PGAS, GOTO, TPIA, CUAN, BRPT, DSSA, BUMI, AADI, ENRG, INDY, MYOH, KINO, LINK, PTIS, SULI, NASI)
  - Sinyal: ARA Hunter, AKUM + SCALPING, SCALPING AWAL, di atas VWAP
  - ARA/ARB dihitung dari penutupan sebelumnya menurut aturan BEI (Kep-00157/BEI/10-2026, 19 Okt–31 Des 2026): ARB 7% untuk saham di atas Rp10; ARA 35% untuk Rp10–Rp200, 25% untuk Rp200–Rp5.000, 20% di atas Rp5.000. Saham Papan Akselerasi memakai ARA/ARB simetris 10% (Rp1 untuk Rp1–Rp10).
  - Daftar preset Papan Akselerasi (25 saham, wajib dicek ulang di aplikasi sekuritas): PACK, PPGL, CASH, CHIP, NANO, WIDI, IDEA, SMKM, RELF, MGLV, KING, KLIN, RUNS, FLMC, IBOS, PLAN, NAYZ, HAJJ, UDNG, FIMP, IPAC, EURO, LUCY, PGJO, AMMS. UVCR BUKAN akselerasi — memakai aturan reguler.

## Cara pakai skrip
```bash
python3 live-screener.py
```

## Catatan penting
- Data bukan feed langsung BEI dan bukan real-time per tick: data publik Yahoo Finance IDX.
- Hasil screening adalah screening, bukan rekomendasi pasti dan bukan jaminan keuntungan.
- Versi web lengkap (Analyzer, FAST, Bandar, Multibagger, Simulasi, kartu sinyal, dan poster full analisis) berjalan sebagai aplikasi web dengan watermark "Sanxzk Ai".
