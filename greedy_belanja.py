"""
===========================================================================
  IMPLEMENTASI ALGORITMA GREEDY
  Optimasi Pembelanjaan Berbasis Prioritas dan Batas Anggaran
  ─────────────────────────────────────────────────────────
  Kriteria Greedy : Rasio = Prioritas / Harga  (semakin tinggi = lebih baik)
  Urutan Seleksi  : Descending rasio → pilih barang selama budget mencukupi
===========================================================================
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ─────────────────────────────────────────────────────────────────────────────
#  DATASET (28 barang, harga realistis pasar Indonesia 2024–2025)
# ─────────────────────────────────────────────────────────────────────────────
dataset = [
    # ── Kebutuhan Pokok (prioritas 9–10) ─────────────────────────────────────
    {"nama_barang": "Beras 5kg",           "kategori": "Makanan",    "harga": 72000, "prioritas": 10},
    {"nama_barang": "Air Minum Galon",     "kategori": "Lainnya",    "harga": 20000, "prioritas": 10},
    {"nama_barang": "Gas LPG 3kg",         "kategori": "Lainnya",    "harga": 21000, "prioritas":  9},
    {"nama_barang": "Telur Ayam 1kg",      "kategori": "Makanan",    "harga": 28000, "prioritas":  9},
    {"nama_barang": "Minyak Goreng 1L",    "kategori": "Makanan",    "harga": 18000, "prioritas":  9},
    {"nama_barang": "Gula Pasir 1kg",      "kategori": "Makanan",    "harga": 17000, "prioritas":  8},
    {"nama_barang": "Garam Halus 250g",    "kategori": "Makanan",    "harga":  5000, "prioritas":  8},
    {"nama_barang": "Ayam Potong 1kg",     "kategori": "Makanan",    "harga": 35000, "prioritas":  8},
    # ── Kebutuhan Kebersihan (prioritas 7–9) ─────────────────────────────────
    {"nama_barang": "Sabun Mandi Batang",  "kategori": "Kebersihan", "harga":  5000, "prioritas":  9},
    {"nama_barang": "Pasta Gigi 75g",      "kategori": "Kebersihan", "harga": 10000, "prioritas":  9},
    {"nama_barang": "Sikat Gigi",          "kategori": "Kebersihan", "harga":  8000, "prioritas":  8},
    {"nama_barang": "Sabun Cuci Piring",   "kategori": "Kebersihan", "harga":  9000, "prioritas":  8},
    {"nama_barang": "Deterjen Bubuk 800g", "kategori": "Kebersihan", "harga": 21000, "prioritas":  7},
    {"nama_barang": "Shampo 170ml",        "kategori": "Kebersihan", "harga": 18000, "prioritas":  7},
    {"nama_barang": "Pembalut Wanita",     "kategori": "Kebersihan", "harga": 15000, "prioritas":  7},
    {"nama_barang": "Tisu Gulung 4pcs",    "kategori": "Kebersihan", "harga": 14000, "prioritas":  6},
    {"nama_barang": "Cairan Antiseptik",   "kategori": "Kebersihan", "harga": 12000, "prioritas":  6},
    # ── Kebutuhan Sekunder (prioritas 4–6) ───────────────────────────────────
    {"nama_barang": "Tahu 5 pcs",          "kategori": "Makanan",    "harga": 10000, "prioritas":  6},
    {"nama_barang": "Tempe 1 papan",       "kategori": "Makanan",    "harga":  8000, "prioritas":  6},
    {"nama_barang": "Ikan Asin 250g",      "kategori": "Makanan",    "harga": 15000, "prioritas":  5},
    {"nama_barang": "Susu UHT 1L",         "kategori": "Makanan",    "harga": 17000, "prioritas":  5},
    {"nama_barang": "Mi Instan (5pcs)",    "kategori": "Makanan",    "harga": 15000, "prioritas":  4},
    {"nama_barang": "Tepung Terigu 1kg",   "kategori": "Makanan",    "harga": 13000, "prioritas":  4},
    {"nama_barang": "Kecap Manis 135ml",   "kategori": "Makanan",    "harga":  8000, "prioritas":  4},
    {"nama_barang": "Kopi Sachet (10pcs)", "kategori": "Makanan",    "harga": 18000, "prioritas":  4},
    # ── Barang Kurang Penting (prioritas 1–3) ────────────────────────────────
    {"nama_barang": "Korek Api",           "kategori": "Lainnya",    "harga":  3000, "prioritas":  3},
    {"nama_barang": "Kantong Plastik",     "kategori": "Lainnya",    "harga":  7000, "prioritas":  2},
    {"nama_barang": "Snack Keripik",       "kategori": "Makanan",    "harga": 12000, "prioritas":  1},
]

# ─────────────────────────────────────────────────────────────────────────────
#  LANGKAH 1 : Hitung rasio otomatis
# ─────────────────────────────────────────────────────────────────────────────
for item in dataset:
    item["rasio"] = round(item["prioritas"] / item["harga"] * 1000, 6)   # ×1000 agar mudah dibaca

# ─────────────────────────────────────────────────────────────────────────────
#  LANGKAH 2 : Urutkan descending berdasarkan rasio
# ─────────────────────────────────────────────────────────────────────────────
dataset_sorted = sorted(dataset, key=lambda x: x["rasio"], reverse=True)

# ─────────────────────────────────────────────────────────────────────────────
#  FUNGSI UTAMA GREEDY
# ─────────────────────────────────────────────────────────────────────────────
def algoritma_greedy(items_sorted: list, budget: int) -> tuple:
    """
    Pilih barang berdasarkan rasio tertinggi hingga budget habis.
    Mengembalikan (list barang terpilih, total biaya).
    """
    selected = []
    total    = 0
    for item in items_sorted:
        if total + item["harga"] <= budget:
            selected.append(item)
            total += item["harga"]
    return selected, total

# ─────────────────────────────────────────────────────────────────────────────
#  CETAK DATASET TERURUT
# ─────────────────────────────────────────────────────────────────────────────
SEP  = "═" * 82
SEP2 = "─" * 82

print(SEP)
print("  DATASET BARANG — DIURUTKAN BERDASARKAN RASIO (Prioritas / Harga × 1000)")
print(SEP)
print(f"  {'No.':<4} {'Nama Barang':<24} {'Kategori':<11} {'Harga':>10}  {'Prior':>5}  {'Rasio':>10}")
print(f"  {SEP2}")

for i, item in enumerate(dataset_sorted, 1):
    print(f"  {i:<4} {item['nama_barang']:<24} {item['kategori']:<11} "
          f"Rp {item['harga']:>8,}  {item['prioritas']:>5}  {item['rasio']:>10.6f}"
          .replace(",", "."))

# ─────────────────────────────────────────────────────────────────────────────
#  SKENARIO BUDGET & OUTPUT GREEDY
# ─────────────────────────────────────────────────────────────────────────────
budgets = [50_000, 100_000, 150_000, 200_000, 300_000]
summary = []   # untuk tabel ringkasan & grafik

for budget in budgets:
    selected, total = algoritma_greedy(dataset_sorted, budget)
    total_prioritas  = sum(i["prioritas"] for i in selected)
    sisa             = budget - total

    print(f"\n{SEP}")
    print(f"  SKENARIO  —  Budget: Rp {budget:,}".replace(",", "."))
    print(SEP)
    print(f"  {'No.':<4} {'Nama Barang':<24} {'Harga':>10}  {'Prior':>5}  {'Rasio':>10}")
    print(f"  {SEP2}")

    for j, item in enumerate(selected, 1):
        print(f"  {j:<4} {item['nama_barang']:<24} "
              f"Rp {item['harga']:>8,}  {item['prioritas']:>5}  {item['rasio']:>10.6f}"
              .replace(",", "."))

    print(f"  {SEP2}")
    print(f"  Jumlah item     : {len(selected)} barang")
    print(f"  Total biaya     : Rp {total:,}".replace(",", "."))
    print(f"  Total prioritas : {total_prioritas}")
    print(f"  Sisa budget     : Rp {sisa:,}".replace(",", "."))

    summary.append({
        "budget":          budget,
        "jumlah_item":     len(selected),
        "total_biaya":     total,
        "total_prioritas": total_prioritas,
        "sisa_budget":     sisa,
    })

# ─────────────────────────────────────────────────────────────────────────────
#  TABEL RINGKASAN
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  TABEL RINGKASAN SEMUA SKENARIO")
print(SEP)
print(f"  {'No.':<4} {'Budget':>12}  {'Jumlah Item':>11}  {'Total Biaya':>13}  "
      f"{'Total Prior':>11}  {'Sisa Budget':>12}")
print(f"  {SEP2}")
for k, s in enumerate(summary, 1):
    print(f"  {k:<4} Rp {s['budget']:>9,}  {s['jumlah_item']:>11}  "
          f"Rp {s['total_biaya']:>10,}  {s['total_prioritas']:>11}  "
          f"Rp {s['sisa_budget']:>9,}".replace(",", "."))
print(SEP)

# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISASI
# ─────────────────────────────────────────────────────────────────────────────
labels      = [f"Rp {s['budget']//1000}rb" for s in summary]
tot_pri     = [s["total_prioritas"] for s in summary]
jml_item    = [s["jumlah_item"]     for s in summary]
tot_biaya   = [s["total_biaya"]     for s in summary]
sisa_budget = [s["sisa_budget"]     for s in summary]
x           = range(len(budgets))

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle(
    "Implementasi Algoritma Greedy — Optimasi Pembelanjaan\nBerbasis Prioritas dan Batas Anggaran",
    fontsize=13, fontweight="bold"
)

# ── Chart 1: Budget vs Total Prioritas ──
ax1 = axes[0, 0]
bars = ax1.bar(x, tot_pri)
ax1.set_title("Budget vs Total Prioritas", fontweight="bold")
ax1.set_xticks(x);  ax1.set_xticklabels(labels)
ax1.set_ylabel("Total Nilai Prioritas")
ax1.set_ylim(0, max(tot_pri) * 1.18)
ax1.grid(axis="y", alpha=0.35, linestyle="--")
for bar, v in zip(bars, tot_pri):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             str(v), ha="center", va="bottom", fontweight="bold")

# ── Chart 2: Budget vs Jumlah Item ──
ax2 = axes[0, 1]
bars2 = ax2.bar(x, jml_item)
ax2.set_title("Budget vs Jumlah Item Terpilih", fontweight="bold")
ax2.set_xticks(x);  ax2.set_xticklabels(labels)
ax2.set_ylabel("Jumlah Barang")
ax2.set_ylim(0, max(jml_item) * 1.2)
ax2.grid(axis="y", alpha=0.35, linestyle="--")
for bar, v in zip(bars2, jml_item):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             str(v), ha="center", va="bottom", fontweight="bold")

# ── Chart 3: Budget vs Total Biaya ──
ax3 = axes[1, 0]
ax3.plot(labels, tot_biaya, marker="o", linewidth=2)
ax3.plot(labels, list(budgets), marker="s", linestyle="--", linewidth=1.5, label="Budget Tersedia")
ax3.set_title("Budget Tersedia vs Total Biaya", fontweight="bold")
ax3.set_ylabel("Nominal (Rp)")
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"Rp {int(v)//1000}rb"))
ax3.legend(fontsize=8)
ax3.grid(alpha=0.35, linestyle="--")

# ── Chart 4: Sisa Budget ──
ax4 = axes[1, 1]
bars4 = ax4.bar(x, sisa_budget)
ax4.set_title("Sisa Budget Setelah Pembelanjaan", fontweight="bold")
ax4.set_xticks(x);  ax4.set_xticklabels(labels)
ax4.set_ylabel("Sisa (Rp)")
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"Rp {int(v)//1000}rb"))
ax4.grid(axis="y", alpha=0.35, linestyle="--")
for bar, v in zip(bars4, sisa_budget):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
             f"Rp {v//1000}rb", ha="center", va="bottom", fontsize=8)

plt.tight_layout()
plt.savefig("grafik_greedy_revisi.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nGrafik disimpan: grafik_greedy_revisi.png")
