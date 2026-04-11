"""
===========================================================================
  CHATBOT TELEGRAM — OPTIMASI PEMBELANJAAN ALGORITMA GREEDY
  dengan CONSTRAINT PRIORITAS
  ─────────────────────────────────────────────────────────
  Algoritma 2 Tahap:
    Tahap 1 (WAJIB)  → Prioritas ≥ 9, urut harga termurah
    Tahap 2 (GREEDY) → Rasio prioritas/harga tertinggi

  Perintah:
    /start           → Menu utama
    /input           → Panduan & mode input
    /tambah          → Tambah barang satu per satu
    /daftar          → Lihat semua barang user
    /budget 100000   → Jalankan algoritma greedy
    /laporan         → Riwayat semua simulasi
    /reset           → Hapus semua data user

  Instalasi:
    pip install python-telegram-bot

  Cara pakai:
    1. Buat bot lewat @BotFather di Telegram → copy token
    2. Tempel token ke variabel BOT_TOKEN di bawah
    3. Jalankan: python bot_greedy_constraint.py
===========================================================================
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ─────────────────────────────────────────────────────────────────────────────
#  KONFIGURASI BOT
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8608995657:AAH7C9KP2bm0OlgGOd7_PNAK8zTb0zoN57Y"   # ← ganti dengan token @BotFather

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  STATE UNTUK ConversationHandler
# ─────────────────────────────────────────────────────────────────────────────
PILIH_MODE, TUNGGU_INPUT = range(2)

# ─────────────────────────────────────────────────────────────────────────────
#  DATASET DEFAULT (28 barang, langsung tersedia)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_DATASET = [
    # ── Prioritas 9–10: Kebutuhan Utama (WAJIB) ──────────────────────────
    {"nama_barang": "Beras 5kg",           "kategori": "Makanan",    "harga": 72000, "prioritas": 10},
    {"nama_barang": "Air Minum Galon",     "kategori": "Lainnya",    "harga": 20000, "prioritas": 10},
    {"nama_barang": "Gas LPG 3kg",         "kategori": "Lainnya",    "harga": 21000, "prioritas": 10},
    {"nama_barang": "Telur Ayam 1kg",      "kategori": "Makanan",    "harga": 28000, "prioritas":  9},
    {"nama_barang": "Minyak Goreng 1L",    "kategori": "Makanan",    "harga": 18000, "prioritas":  9},
    {"nama_barang": "Garam 250g",          "kategori": "Makanan",    "harga":  5000, "prioritas":  9},
    {"nama_barang": "Sabun Mandi",         "kategori": "Kebersihan", "harga":  5000, "prioritas":  9},
    {"nama_barang": "Pasta Gigi 75g",      "kategori": "Kebersihan", "harga": 10000, "prioritas":  9},
    # ── Prioritas 6–8: Kebutuhan Penting (GREEDY) ────────────────────────
    {"nama_barang": "Gula Pasir 1kg",      "kategori": "Makanan",    "harga": 17000, "prioritas":  8},
    {"nama_barang": "Ayam Potong 1kg",     "kategori": "Makanan",    "harga": 35000, "prioritas":  8},
    {"nama_barang": "Sikat Gigi",          "kategori": "Kebersihan", "harga":  8000, "prioritas":  8},
    {"nama_barang": "Sabun Cuci Piring",   "kategori": "Kebersihan", "harga":  9000, "prioritas":  8},
    {"nama_barang": "Tahu 5 pcs",          "kategori": "Makanan",    "harga": 10000, "prioritas":  7},
    {"nama_barang": "Tempe 1 papan",       "kategori": "Makanan",    "harga":  8000, "prioritas":  7},
    {"nama_barang": "Deterjen 800g",       "kategori": "Kebersihan", "harga": 21000, "prioritas":  7},
    {"nama_barang": "Shampo 170ml",        "kategori": "Kebersihan", "harga": 18000, "prioritas":  7},
    {"nama_barang": "Pembalut Wanita",     "kategori": "Kebersihan", "harga": 15000, "prioritas":  7},
    {"nama_barang": "Ikan Asin 250g",      "kategori": "Makanan",    "harga": 15000, "prioritas":  6},
    {"nama_barang": "Tisu Gulung 4pcs",    "kategori": "Kebersihan", "harga": 14000, "prioritas":  6},
    {"nama_barang": "Cairan Antiseptik",   "kategori": "Kebersihan", "harga": 12000, "prioritas":  6},
    # ── Prioritas 1–5: Kebutuhan Tambahan (GREEDY) ───────────────────────
    {"nama_barang": "Susu UHT 1L",         "kategori": "Makanan",    "harga": 17000, "prioritas":  5},
    {"nama_barang": "Tepung Terigu 1kg",   "kategori": "Makanan",    "harga": 13000, "prioritas":  4},
    {"nama_barang": "Mi Instan (5pcs)",    "kategori": "Makanan",    "harga": 15000, "prioritas":  4},
    {"nama_barang": "Kecap Manis 135ml",   "kategori": "Makanan",    "harga":  8000, "prioritas":  4},
    {"nama_barang": "Kopi Sachet (10pcs)", "kategori": "Makanan",    "harga": 18000, "prioritas":  3},
    {"nama_barang": "Korek Api",           "kategori": "Lainnya",    "harga":  3000, "prioritas":  3},
    {"nama_barang": "Kantong Plastik",     "kategori": "Lainnya",    "harga":  7000, "prioritas":  2},
    {"nama_barang": "Snack Keripik",       "kategori": "Makanan",    "harga": 12000, "prioritas":  1},
]

# ─────────────────────────────────────────────────────────────────────────────
#  PENYIMPANAN DATA USER (in-memory, per user_id)
#
#  Struktur:
#    user_store[user_id] = {
#        "barang"  : [...],   # list barang (default + tambahan user)
#        "riwayat" : [...],   # list hasil simulasi budget
#        "mode"    : str,     # "harian" / "mingguan" / "bulanan"
#    }
# ─────────────────────────────────────────────────────────────────────────────
user_store: dict[int, dict] = {}


def get_user(user_id: int) -> dict:
    """Ambil atau inisiasi data user dengan dataset default."""
    if user_id not in user_store:
        user_store[user_id] = {
            "barang":  [dict(item) for item in DEFAULT_DATASET],
            "riwayat": [],
            "mode":    "harian",
        }
    return user_store[user_id]


# ─────────────────────────────────────────────────────────────────────────────
#  ALGORITMA GREEDY 2 TAHAP
# ─────────────────────────────────────────────────────────────────────────────

def algoritma_greedy_constraint(items: list, budget: int) -> tuple:
    """
    Algoritma Greedy dengan Constraint Prioritas (2 Tahap).

    Tahap 1 – WAJIB:
      Pilih barang dengan prioritas ≥ 9, diurutkan dari harga termurah.
      Tujuan: memastikan kebutuhan utama (beras, air, gas) selalu terbeli.

    Tahap 2 – GREEDY:
      Dari sisa barang, hitung rasio = prioritas / harga.
      Urutkan descending, pilih selama budget mencukupi.

    Return: (barang_terpilih, total_biaya)
    """
    selected       = []
    sisa_budget    = budget
    terpilih_nama  = set()

    # ── TAHAP 1: WAJIB ───────────────────────────────────────────────────
    barang_wajib = sorted(
        [item for item in items if item["prioritas"] >= 9],
        key=lambda x: x["harga"]   # termurah dulu
    )
    for item in barang_wajib:
        if sisa_budget >= item["harga"]:
            dipilih = dict(item)
            dipilih["tahap"] = "Wajib"
            selected.append(dipilih)
            terpilih_nama.add(item["nama_barang"])
            sisa_budget -= item["harga"]

    # ── TAHAP 2: GREEDY ──────────────────────────────────────────────────
    sisa_barang = [
        item for item in items
        if item["nama_barang"] not in terpilih_nama
    ]
    # Hitung dan urutkan berdasarkan rasio
    for item in sisa_barang:
        item["rasio"] = item["prioritas"] / item["harga"]

    sisa_barang_sorted = sorted(sisa_barang, key=lambda x: x["rasio"], reverse=True)

    for item in sisa_barang_sorted:
        if sisa_budget >= item["harga"]:
            dipilih = dict(item)
            dipilih["tahap"] = "Greedy"
            selected.append(dipilih)
            sisa_budget -= item["harga"]

    total_biaya = budget - sisa_budget
    return selected, total_biaya


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITAS FORMAT
# ─────────────────────────────────────────────────────────────────────────────

def rp(nominal: int) -> str:
    return f"Rp {nominal:,}".replace(",", ".")


def parse_input_barang(teks: str) -> dict | None:
    """
    Parse berbagai format input barang dari user.

    Format yang didukung:
      (A) nama harga prioritas
          contoh: "sabun 15000 9"
      (B) nama harga
          contoh: "beras 72000"   → prioritas akan ditanya
      (C) beras 72000 prioritas 10
      (D) 3 sabun 15000   (angka depan = prioritas)

    Return dict atau None jika tidak bisa di-parse.
    """
    token = teks.strip().split()

    # Format D: angka_depan nama harga
    if len(token) >= 3 and token[0].isdigit():
        try:
            prioritas  = int(token[0])
            nama_barang = " ".join(token[1:-1])
            harga      = int(token[-1])
            if 1 <= prioritas <= 10 and harga > 0:
                return {"nama_barang": nama_barang, "harga": harga,
                        "prioritas": prioritas, "kategori": "Lainnya"}
        except ValueError:
            pass

    # Format C: nama harga prioritas NNN
    if "prioritas" in token:
        try:
            idx_p = token.index("prioritas")
            prioritas   = int(token[idx_p + 1])
            harga_token = [t for t in token[:idx_p] if t.isdigit()]
            nama_token  = [t for t in token[:idx_p] if not t.isdigit()]
            nama_barang = " ".join(nama_token)
            harga       = int(harga_token[-1])
            if 1 <= prioritas <= 10 and harga > 0 and nama_barang:
                return {"nama_barang": nama_barang, "harga": harga,
                        "prioritas": prioritas, "kategori": "Lainnya"}
        except (ValueError, IndexError):
            pass

    # Format A: nama harga prioritas
    if len(token) >= 3:
        try:
            harga     = int(token[-2])
            prioritas = int(token[-1])
            nama_barang = " ".join(token[:-2])
            if 1 <= prioritas <= 10 and harga > 0 and nama_barang:
                return {"nama_barang": nama_barang, "harga": harga,
                        "prioritas": prioritas, "kategori": "Lainnya"}
        except ValueError:
            pass

    # Format B: nama harga (prioritas default 5)
    if len(token) >= 2:
        try:
            harga       = int(token[-1])
            nama_barang = " ".join(token[:-1])
            if harga > 0 and nama_barang:
                return {"nama_barang": nama_barang, "harga": harga,
                        "prioritas": 5, "kategori": "Lainnya",
                        "_default_prioritas": True}
        except ValueError:
            pass

    return None


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /start
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ud   = get_user(user.id)

    pesan = (
        f"👋 Halo, *{user.first_name}*!\n\n"
        "🛒 *Sistem Optimasi Belanja — Algoritma Greedy*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Bot ini memilih barang belanjaan secara *cerdas* menggunakan "
        "*Algoritma Greedy 2 Tahap*:\n\n"
        "🔴 *Tahap 1 – WAJIB*\n"
        "    Barang prioritas ≥ 9 dipilih lebih dulu\n"
        "    (beras, air, gas, telur, dll)\n\n"
        "🟢 *Tahap 2 – GREEDY*\n"
        "    Sisa budget dioptimalkan berdasarkan\n"
        "    rasio Prioritas / Harga tertinggi\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Daftar Perintah:*\n"
        "▸ /start            → Menu ini\n"
        "▸ /input            → Panduan & pilih mode belanja\n"
        "▸ /tambah           → Tambah barang ke daftar\n"
        "▸ /daftar           → Lihat semua barang\n"
        "▸ /budget `<nominal>` → Hitung rekomendasi belanja\n"
        "    contoh: `/budget 100000`\n"
        "▸ /laporan          → Riwayat semua simulasi\n"
        "▸ /reset            → Hapus data & mulai ulang\n\n"
        f"📦 Dataset default *{len(ud['barang'])} barang* sudah siap.\n"
        "Langsung coba: `/budget 150000`"
    )
    await update.message.reply_text(pesan, parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /input → ConversationHandler (pilih mode)
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_input_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan panduan format dan keyboard pilihan mode."""
    keyboard = [["🌅 Harian", "📅 Mingguan", "📆 Bulanan"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    pesan = (
        "📝 *Panduan Input Barang*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Format yang didukung:\n\n"
        "```\n"
        "nama harga prioritas\n"
        "Contoh: sabun 15000 9\n"
        "```\n"
        "```\n"
        "prioritas nama harga\n"
        "Contoh: 3 sabun 15000\n"
        "```\n"
        "```\n"
        "nama harga prioritas N\n"
        "Contoh: beras 72000 prioritas 10\n"
        "```\n\n"
        "📌 *Skala Prioritas:*\n"
        "🔴 `9–10` = Kebutuhan utama/pokok\n"
        "🟡 `6–8`  = Kebutuhan penting\n"
        "🟢 `1–5`  = Kebutuhan tambahan\n\n"
        "Pilih *mode belanja* kamu:"
    )
    await update.message.reply_text(pesan, parse_mode="Markdown",
                                    reply_markup=reply_markup)
    return PILIH_MODE


async def cmd_input_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simpan mode yang dipilih, lanjut ke state input barang."""
    teks = update.message.text.strip().lower()
    uid  = update.effective_user.id
    ud   = get_user(uid)

    if   "harian"   in teks: ud["mode"] = "harian";   label = "🌅 Harian"
    elif "mingguan" in teks: ud["mode"] = "mingguan"; label = "📅 Mingguan"
    elif "bulanan"  in teks: ud["mode"] = "bulanan";  label = "📆 Bulanan"
    else:                    ud["mode"] = "harian";   label = "🌅 Harian (default)"

    await update.message.reply_text(
        f"✅ Mode *{label}* dipilih.\n\n"
        "Sekarang kirim data barang dalam format:\n"
        "`nama harga prioritas`\n"
        "Contoh: `sabun 15000 9`\n\n"
        "Ketik /selesai jika sudah selesai input, atau /batal untuk membatalkan.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TUNGGU_INPUT


async def cmd_input_barang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proses input barang — bisa satu baris atau banyak baris sekaligus."""
    teks = update.message.text.strip()
    uid  = update.effective_user.id
    ud   = get_user(uid)

    baris_list = [b.strip() for b in teks.splitlines() if b.strip()]

    berhasil = []
    gagal    = []

    for baris in baris_list:
        item = parse_input_barang(baris)
        if item:
            ud["barang"].append(item)
            berhasil.append(item)
        else:
            gagal.append(baris)

    pesan = ""

    if berhasil:
        pesan += f"✅ *{len(berhasil)} barang ditambahkan:*\n"
        for item in berhasil:
            if   item["prioritas"] >= 9: level = "🔴"
            elif item["prioritas"] >= 6: level = "🟡"
            else:                        level = "🟢"
            pesan += f"  {level} *{item['nama_barang']}* — {rp(item['harga'])} | ⭐{item['prioritas']}\n"

    if gagal:
        pesan += f"\n❌ *{len(gagal)} baris tidak dikenali:*\n"
        for b in gagal:
            pesan += f"  `{b}`\n"
        pesan += "\nFormat: `nama harga prioritas`  contoh: `sabun 15000 9`\n"

    pesan += f"\n📦 Total barang: *{len(ud['barang'])}*\n"
    pesan += "/selesai → Tutup sesi input | /batal → Batalkan"

    await update.message.reply_text(pesan, parse_mode="Markdown")
    return TUNGGU_INPUT


async def cmd_input_selesai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)
    await update.message.reply_text(
        f"✅ *{len(ud['barang'])} barang tersimpan!*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    # Langsung tampilkan menu utama
    await cmd_start(update, context)
    return ConversationHandler.END


async def cmd_batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❎ Sesi input dibatalkan.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /tambah (input cepat satu barang)
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_tambah_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ *Tambah Barang*\n\n"
        "Kirim data barang dalam format:\n"
        "`nama harga prioritas`\n\n"
        "Contoh:\n"
        "`Indomie Goreng 3500 4`\n"
        "`9 Beras 5kg 72000`\n"
        "`Susu 17000 prioritas 5`\n\n"
        "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown",
    )
    return TUNGGU_INPUT


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /daftar
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)
    items = ud["barang"]

    if not items:
        await update.message.reply_text(
            "📭 Daftar barang kosong.\nGunakan /tambah untuk menambah barang."
        )
        return

    n_utama   = sum(1 for i in items if i["prioritas"] >= 9)
    n_penting = sum(1 for i in items if 6 <= i["prioritas"] <= 8)
    n_tambahan = sum(1 for i in items if i["prioritas"] <= 5)

    baris = [
        f"📋 *Daftar Barang* ({len(items)} item | Mode: {ud['mode'].capitalize()})",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🔴 Utama: {n_utama}  |  🟡 Penting: {n_penting}  |  🟢 Tambahan: {n_tambahan}",
        "────────────────────────",
    ]

    # Pecah menjadi max 2 pesan jika barang banyak
    for i, item in enumerate(items, 1):
        if   item["prioritas"] >= 9: ikon = "🔴"
        elif item["prioritas"] >= 6: ikon = "🟡"
        else:                        ikon = "🟢"
        baris.append(
            f"{i:>2}. {ikon} *{item['nama_barang']}*\n"
            f"    💰 {rp(item['harga'])}  |  ⭐ Prioritas: {item['prioritas']}"
        )

    # Kirim dalam satu atau dua pesan (batas 4096 karakter Telegram)
    teks = "\n".join(baris)
    if len(teks) <= 4000:
        await update.message.reply_text(teks, parse_mode="Markdown")
    else:
        mid = len(items) // 2
        await update.message.reply_text(
            "\n".join(baris[:4 + mid]), parse_mode="Markdown"
        )
        await update.message.reply_text(
            "\n".join(baris[4 + mid:]), parse_mode="Markdown"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /budget <nominal>
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)

    # ── Validasi argumen ──
    if not context.args or not context.args[0].replace(".", "").replace(",", "").isdigit():
        await update.message.reply_text(
            "⚠️ Format: `/budget <nominal>`\n"
            "Contoh: `/budget 100000`",
            parse_mode="Markdown",
        )
        return

    budget = int(context.args[0].replace(".", "").replace(",", ""))
    if budget <= 0:
        await update.message.reply_text("❌ Budget harus lebih dari 0.")
        return

    items = ud["barang"]
    if not items:
        await update.message.reply_text(
            "📭 Daftar barang kosong.\nGunakan /tambah untuk menambah barang."
        )
        return

    # ── Jalankan algoritma ──
    selected, total = algoritma_greedy_constraint(items, budget)
    total_pri = sum(i["prioritas"] for i in selected)
    sisa      = budget - total
    n_wajib   = sum(1 for i in selected if i["tahap"] == "Wajib")
    n_greedy  = sum(1 for i in selected if i["tahap"] == "Greedy")

    # Simpan ke riwayat
    ud["riwayat"].append({
        "budget":          budget,
        "mode":            ud["mode"],
        "jumlah_item":     len(selected),
        "n_wajib":         n_wajib,
        "n_greedy":        n_greedy,
        "total_biaya":     total,
        "total_prioritas": total_pri,
        "sisa_budget":     sisa,
        "barang_terpilih": [i["nama_barang"] for i in selected],
    })

    # ── Format output ──
    baris = [
        "🛒 *Rekomendasi Belanja — Algoritma Greedy*",
        f"💰 Budget  : *{rp(budget)}*  |  Mode: {ud['mode'].capitalize()}",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if not selected:
        baris.append("😔 Tidak ada barang yang dapat dibeli dengan budget ini.")
    else:
        # Tahap 1
        if n_wajib > 0:
            baris.append("🔴 *TAHAP 1 — PRIORITAS WAJIB (≥9)*")
            for j, item in enumerate([i for i in selected if i["tahap"] == "Wajib"], 1):
                baris.append(
                    f"  {j}. *{item['nama_barang']}*\n"
                    f"     💰 {rp(item['harga'])}  |  ⭐ {item['prioritas']}"
                )

        # Tahap 2
        if n_greedy > 0:
            baris.append("🟢 *TAHAP 2 — GREEDY (Rasio P/H)*")
            for j, item in enumerate([i for i in selected if i["tahap"] == "Greedy"], 1):
                rasio = round(item.get("rasio", item["prioritas"] / item["harga"]) * 1000, 2)
                baris.append(
                    f"  {j}. *{item['nama_barang']}*\n"
                    f"     💰 {rp(item['harga'])}  |  ⭐ {item['prioritas']}  |  📊 {rasio:.2f}"
                )

        # Ringkasan
        eff = round(total / budget * 100, 1)
        baris += [
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📦 Jumlah item      : *{len(selected)}* ({n_wajib} wajib + {n_greedy} greedy)",
            f"💳 Total biaya      : *{rp(total)}*",
            f"⭐ Total prioritas  : *{total_pri}*",
            f"💵 Sisa budget      : *{rp(sisa)}*",
            f"📈 Efisiensi budget : *{eff}%*",
        ]

    teks = "\n".join(baris)
    # Kirim dalam satu atau dua pesan jika terlalu panjang
    if len(teks) <= 4000:
        await update.message.reply_text(teks, parse_mode="Markdown")
    else:
        mid = len(selected) // 2
        await update.message.reply_text("\n".join(baris[:6 + n_wajib + 1]), parse_mode="Markdown")
        await update.message.reply_text("\n".join(baris[6 + n_wajib + 1:]), parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /laporan
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)
    riwayat = ud["riwayat"]

    if not riwayat:
        await update.message.reply_text(
            "📭 Belum ada simulasi yang dijalankan.\n"
            "Gunakan `/budget <nominal>` untuk memulai.",
            parse_mode="Markdown",
        )
        return

    total_pengeluaran = sum(r["total_biaya"] for r in riwayat)

    baris = [
        "📊 *LAPORAN RIWAYAT SIMULASI*",
        f"Total simulasi  : *{len(riwayat)}x*",
        f"Total pengeluaran: *{rp(total_pengeluaran)}*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    for k, r in enumerate(riwayat, 1):
        eff = round(r["total_biaya"] / r["budget"] * 100, 1)
        baris.append(
            f"*Simulasi {k}* [{r['mode'].capitalize()}]\n"
            f"  💰 Budget     : {rp(r['budget'])}\n"
            f"  📦 Item       : {r['jumlah_item']} "
            f"({r['n_wajib']} wajib + {r['n_greedy']} greedy)\n"
            f"  💳 Biaya      : {rp(r['total_biaya'])}\n"
            f"  ⭐ Prioritas  : {r['total_prioritas']}\n"
            f"  💵 Sisa       : {rp(r['sisa_budget'])}\n"
            f"  📈 Efisiensi  : {eff}%"
        )
        if k < len(riwayat):
            baris.append("────────────────────────")

    # Simulasi terbaik (efisiensi prioritas/budget tertinggi)
    best = max(riwayat, key=lambda x: x["total_prioritas"] / x["budget"])
    baris += [
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏆 *Simulasi terbaik*:\n"
        f"   Budget {rp(best['budget'])} → Prioritas/Budget = "
        f"{best['total_prioritas']/best['budget']*1000:.4f}",
    ]

    teks = "\n".join(baris)
    if len(teks) <= 4000:
        await update.message.reply_text(teks, parse_mode="Markdown")
    else:
        # Kirim per blok 3 simulasi
        chunk = [baris[:4]]
        blok  = []
        for b in baris[4:]:
            blok.append(b)
            if "━━━" in b and blok:
                chunk.append(blok); blok = []
        if blok:
            chunk.append(blok)
        for c in chunk:
            await update.message.reply_text("\n".join(c), parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /reset
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_store.pop(uid, None)   # hapus semua data user
    await update.message.reply_text(
        "🔄 *Data berhasil direset!*\n\n"
        f"Dataset default *{len(DEFAULT_DATASET)} barang* dimuat ulang.\n"
        "Gunakan /start untuk melihat menu.",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: pesan tidak dikenal
# ─────────────────────────────────────────────────────────────────────────────
async def pesan_tidak_dikenal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Perintah tidak dikenali.\n"
        "Ketik /start untuk melihat semua perintah yang tersedia."
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN — JALANKAN BOT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("🤖 Bot Greedy Constraint mulai berjalan...")
    print("   Tekan Ctrl+C untuk menghentikan.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    # ── ConversationHandler untuk /input (pilih mode → input barang) ──
    conv_input = ConversationHandler(
        entry_points=[CommandHandler("input", cmd_input_start)],
        states={
            PILIH_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_input_mode),
            ],
            TUNGGU_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_input_barang),
                CommandHandler("selesai", cmd_input_selesai),
                CommandHandler("batal",   cmd_batal),
            ],
        },
        fallbacks=[CommandHandler("batal", cmd_batal)],
    )

    # ── ConversationHandler untuk /tambah (input cepat satu barang) ──
    conv_tambah = ConversationHandler(
    entry_points=[CommandHandler("tambah", cmd_tambah_start)],
    states={
        TUNGGU_INPUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_input_barang),
            CommandHandler("selesai", cmd_input_selesai),
            CommandHandler("batal", cmd_batal),
        ],
    },
    fallbacks=[CommandHandler("batal", cmd_batal)],
)

    # ── Daftarkan semua handler ──
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("daftar",  cmd_daftar))
    app.add_handler(CommandHandler("budget",  cmd_budget))
    app.add_handler(CommandHandler("laporan", cmd_laporan))
    app.add_handler(CommandHandler("reset",   cmd_reset))
    app.add_handler(conv_input)
    app.add_handler(conv_tambah)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, pesan_tidak_dikenal)
    )

    # ── Mulai polling ──
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()