"""
===========================================================================
  CHATBOT TELEGRAM — OPTIMASI PEMBELANJAAN ALGORITMA GREEDY
  ─────────────────────────────────────────────────────────
  Teknologi : Python + python-telegram-bot (v20+, async)
  Perintah  :
    /start         → Menu utama
    /input         → Panduan input data barang
    /tambah        → Tambah barang ke daftar user
    /daftar        → Tampilkan semua barang yang sudah diinput
    /budget 100000 → Jalankan algoritma greedy sesuai budget
    /laporan       → Laporan ringkasan semua skenario yang pernah dijalankan
    /reset         → Hapus semua data user & mulai ulang

  Instalasi  :
    pip install python-telegram-bot

  Cara pakai :
    1. Ganti BOT_TOKEN di bawah dengan token dari @BotFather
    2. Jalankan: python bot_greedy.py
===========================================================================
"""

import json
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# ─────────────────────────────────────────────────────────────────────────────
#  KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = "MASUKKAN_TOKEN_BOT_KAMU_DI_SINI"   # ← ganti dengan token @BotFather

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# State untuk ConversationHandler (input barang)
TUNGGU_INPUT = 1

# ─────────────────────────────────────────────────────────────────────────────
#  DATASET DEFAULT (langsung tersedia tanpa input manual)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_DATASET = [
    {"nama_barang": "Beras 5kg",           "kategori": "Makanan",    "harga": 72000, "prioritas": 10},
    {"nama_barang": "Air Minum Galon",     "kategori": "Lainnya",    "harga": 20000, "prioritas": 10},
    {"nama_barang": "Gas LPG 3kg",         "kategori": "Lainnya",    "harga": 21000, "prioritas":  9},
    {"nama_barang": "Telur Ayam 1kg",      "kategori": "Makanan",    "harga": 28000, "prioritas":  9},
    {"nama_barang": "Minyak Goreng 1L",    "kategori": "Makanan",    "harga": 18000, "prioritas":  9},
    {"nama_barang": "Gula Pasir 1kg",      "kategori": "Makanan",    "harga": 17000, "prioritas":  8},
    {"nama_barang": "Garam Halus 250g",    "kategori": "Makanan",    "harga":  5000, "prioritas":  8},
    {"nama_barang": "Ayam Potong 1kg",     "kategori": "Makanan",    "harga": 35000, "prioritas":  8},
    {"nama_barang": "Sabun Mandi Batang",  "kategori": "Kebersihan", "harga":  5000, "prioritas":  9},
    {"nama_barang": "Pasta Gigi 75g",      "kategori": "Kebersihan", "harga": 10000, "prioritas":  9},
    {"nama_barang": "Sikat Gigi",          "kategori": "Kebersihan", "harga":  8000, "prioritas":  8},
    {"nama_barang": "Sabun Cuci Piring",   "kategori": "Kebersihan", "harga":  9000, "prioritas":  8},
    {"nama_barang": "Deterjen Bubuk 800g", "kategori": "Kebersihan", "harga": 21000, "prioritas":  7},
    {"nama_barang": "Shampo 170ml",        "kategori": "Kebersihan", "harga": 18000, "prioritas":  7},
    {"nama_barang": "Pembalut Wanita",     "kategori": "Kebersihan", "harga": 15000, "prioritas":  7},
    {"nama_barang": "Tisu Gulung 4pcs",    "kategori": "Kebersihan", "harga": 14000, "prioritas":  6},
    {"nama_barang": "Cairan Antiseptik",   "kategori": "Kebersihan", "harga": 12000, "prioritas":  6},
    {"nama_barang": "Tahu 5 pcs",          "kategori": "Makanan",    "harga": 10000, "prioritas":  6},
    {"nama_barang": "Tempe 1 papan",       "kategori": "Makanan",    "harga":  8000, "prioritas":  6},
    {"nama_barang": "Ikan Asin 250g",      "kategori": "Makanan",    "harga": 15000, "prioritas":  5},
    {"nama_barang": "Susu UHT 1L",         "kategori": "Makanan",    "harga": 17000, "prioritas":  5},
    {"nama_barang": "Mi Instan (5pcs)",    "kategori": "Makanan",    "harga": 15000, "prioritas":  4},
    {"nama_barang": "Tepung Terigu 1kg",   "kategori": "Makanan",    "harga": 13000, "prioritas":  4},
    {"nama_barang": "Kecap Manis 135ml",   "kategori": "Makanan",    "harga":  8000, "prioritas":  4},
    {"nama_barang": "Kopi Sachet (10pcs)", "kategori": "Makanan",    "harga": 18000, "prioritas":  4},
    {"nama_barang": "Korek Api",           "kategori": "Lainnya",    "harga":  3000, "prioritas":  3},
    {"nama_barang": "Kantong Plastik",     "kategori": "Lainnya",    "harga":  7000, "prioritas":  2},
    {"nama_barang": "Snack Keripik",       "kategori": "Makanan",    "harga": 12000, "prioritas":  1},
]

# ─────────────────────────────────────────────────────────────────────────────
#  PENYIMPANAN DATA USER (in-memory, per user_id)
#  Struktur: user_data[user_id] = {"barang": [...], "riwayat": [...]}
# ─────────────────────────────────────────────────────────────────────────────
user_data: dict[int, dict] = {}


def get_user(user_id: int) -> dict:
    """Ambil atau inisiasi data user."""
    if user_id not in user_data:
        user_data[user_id] = {
            "barang":  list(DEFAULT_DATASET),   # copy dataset default
            "riwayat": [],                       # riwayat simulasi greedy
        }
    return user_data[user_id]


# ─────────────────────────────────────────────────────────────────────────────
#  ALGORITMA GREEDY
# ─────────────────────────────────────────────────────────────────────────────
def algoritma_greedy(items: list, budget: int) -> tuple:
    """
    Urutkan barang berdasarkan rasio prioritas/harga (descending),
    lalu pilih barang selama budget mencukupi.
    Mengembalikan: (barang_terpilih, total_biaya)
    """
    # Hitung rasio untuk setiap item
    for item in items:
        item["rasio"] = item["prioritas"] / item["harga"]

    # Urutkan descending berdasarkan rasio
    sorted_items = sorted(items, key=lambda x: x["rasio"], reverse=True)

    selected = []
    total    = 0
    for item in sorted_items:
        if total + item["harga"] <= budget:
            selected.append(item)
            total += item["harga"]

    return selected, total


# ─────────────────────────────────────────────────────────────────────────────
#  FORMAT RUPIAH
# ─────────────────────────────────────────────────────────────────────────────
def rp(nominal: int) -> str:
    return f"Rp {nominal:,}".replace(",", ".")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /start
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id)   # inisiasi data user

    pesan = (
        f"👋 Halo, *{user.first_name}*!\n\n"
        "🛒 *Bot Optimasi Belanja — Algoritma Greedy*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Bot ini membantu kamu memilih barang belanjaan secara *optimal* "
        "berdasarkan *prioritas* dan *batas anggaran* menggunakan Algoritma Greedy.\n\n"
        "📋 *Daftar Perintah:*\n"
        "▸ /start — Menu utama\n"
        "▸ /input — Panduan menambah barang\n"
        "▸ /tambah — Tambah barang baru ke daftar\n"
        "▸ /daftar — Lihat semua barang dalam daftar\n"
        "▸ /budget `<nominal>` — Hitung rekomendasi belanja\n"
        "  contoh: `/budget 100000`\n"
        "▸ /laporan — Laporan semua simulasi yang pernah dijalankan\n"
        "▸ /reset — Hapus semua data & mulai ulang\n\n"
        "💡 *Dataset default* 28 barang sudah tersedia.\n"
        "Langsung coba: `/budget 150000`"
    )
    await update.message.reply_text(pesan, parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /input  (panduan format)
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan = (
        "📝 *Panduan Input Barang*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Gunakan perintah `/tambah` lalu ikuti petunjuknya.\n\n"
        "Format yang perlu kamu isi:\n"
        "```\n"
        "nama_barang | harga | prioritas\n"
        "```\n"
        "Contoh:\n"
        "```\n"
        "Indomie Goreng | 3500 | 4\n"
        "```\n\n"
        "📌 *Ketentuan:*\n"
        "• Nama barang: teks bebas\n"
        "• Harga: angka (dalam Rupiah, tanpa titik/koma)\n"
        "• Prioritas: angka *1–10* (10 = sangat penting)\n\n"
        "Skala Prioritas:\n"
        "🔴 9–10 = Kebutuhan pokok\n"
        "🔵 7–8  = Kebersihan penting\n"
        "🟡 4–6  = Kebutuhan sekunder\n"
        "⚪ 1–3  = Kurang penting"
    )
    await update.message.reply_text(pesan, parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /tambah  (ConversationHandler)
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_tambah_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ *Tambah Barang Baru*\n\n"
        "Ketik dalam format:\n"
        "`nama_barang | harga | prioritas`\n\n"
        "Contoh:\n"
        "`Indomie Goreng | 3500 | 4`\n\n"
        "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown",
    )
    return TUNGGU_INPUT


async def cmd_tambah_proses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.strip()
    bagian = [b.strip() for b in teks.split("|")]

    if len(bagian) != 3:
        await update.message.reply_text(
            "❌ Format salah. Gunakan:\n`nama | harga | prioritas`\n\nCoba lagi atau /batal.",
            parse_mode="Markdown",
        )
        return TUNGGU_INPUT

    nama = bagian[0]
    try:
        harga     = int(bagian[1])
        prioritas = int(bagian[2])
        if not (1 <= prioritas <= 10):
            raise ValueError
        if harga <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "❌ Harga harus angka positif, prioritas antara 1–10.\n\nCoba lagi atau /batal.",
            parse_mode="Markdown",
        )
        return TUNGGU_INPUT

    uid = update.effective_user.id
    ud  = get_user(uid)
    ud["barang"].append({
        "nama_barang": nama,
        "kategori":    "Lainnya",
        "harga":       harga,
        "prioritas":   prioritas,
    })

    await update.message.reply_text(
        f"✅ *Barang berhasil ditambahkan!*\n\n"
        f"📦 Nama      : {nama}\n"
        f"💰 Harga     : {rp(harga)}\n"
        f"⭐ Prioritas : {prioritas}/10\n\n"
        f"Total barang dalam daftar: *{len(ud['barang'])}*\n"
        f"Gunakan `/tambah` lagi atau `/budget <nominal>` untuk simulasi.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cmd_batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❎ Input dibatalkan.")
    return ConversationHandler.END


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /daftar
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)
    items = ud["barang"]

    if not items:
        await update.message.reply_text("📭 Daftar barang kosong. Gunakan /tambah untuk menambah.")
        return

    # Tampilkan per halaman (max 20 item per pesan agar tidak terlalu panjang)
    baris = [f"📋 *Daftar Barang ({len(items)} item)*", "━━━━━━━━━━━━━━━━━━━━━━━━"]
    for i, item in enumerate(items, 1):
        baris.append(
            f"{i:>2}. {item['nama_barang']}\n"
            f"    💰 {rp(item['harga'])}  |  ⭐ Prioritas: {item['prioritas']}"
        )
    await update.message.reply_text("\n".join(baris), parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /budget <nominal>
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)

    # Validasi argumen
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Format: `/budget <nominal>`\nContoh: `/budget 100000`",
            parse_mode="Markdown",
        )
        return

    budget = int(context.args[0])
    if budget <= 0:
        await update.message.reply_text("❌ Budget harus lebih dari 0.")
        return

    items = ud["barang"]
    if not items:
        await update.message.reply_text("📭 Daftar barang kosong. Tambah dulu dengan /tambah.")
        return

    # Jalankan greedy
    selected, total = algoritma_greedy(list(items), budget)
    total_pri = sum(i["prioritas"] for i in selected)
    sisa      = budget - total

    # Simpan ke riwayat
    ud["riwayat"].append({
        "budget":          budget,
        "jumlah_item":     len(selected),
        "total_biaya":     total,
        "total_prioritas": total_pri,
        "sisa_budget":     sisa,
    })

    # Format output
    baris = [
        f"🛒 *Rekomendasi Belanja — Algoritma Greedy*",
        f"💰 Budget   : *{rp(budget)}*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if not selected:
        baris.append("😔 Tidak ada barang yang bisa dibeli dengan budget tersebut.")
    else:
        for j, item in enumerate(selected, 1):
            rasio = round(item["prioritas"] / item["harga"] * 1000, 4)
            baris.append(
                f"{j:>2}. *{item['nama_barang']}*\n"
                f"    💰 {rp(item['harga'])}  |  ⭐ {item['prioritas']}  |  📊 Rasio: {rasio:.4f}"
            )
        baris += [
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📦 Jumlah item     : *{len(selected)} barang*",
            f"💳 Total biaya     : *{rp(total)}*",
            f"⭐ Total prioritas : *{total_pri}*",
            f"💵 Sisa budget     : *{rp(sisa)}*",
        ]

    await update.message.reply_text("\n".join(baris), parse_mode="Markdown")


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
            "Gunakan `/budget <nominal>` terlebih dahulu.",
            parse_mode="Markdown",
        )
        return

    baris = [
        "📊 *LAPORAN SIMULASI GREEDY*",
        f"Total simulasi dijalankan: *{len(riwayat)}x*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for k, r in enumerate(riwayat, 1):
        eff = round(r["total_biaya"] / r["budget"] * 100, 1)
        baris.append(
            f"*Simulasi {k}*\n"
            f"  💰 Budget       : {rp(r['budget'])}\n"
            f"  📦 Jumlah item  : {r['jumlah_item']} barang\n"
            f"  💳 Total biaya  : {rp(r['total_biaya'])}\n"
            f"  ⭐ Total prior  : {r['total_prioritas']}\n"
            f"  💵 Sisa         : {rp(r['sisa_budget'])}\n"
            f"  📈 Efisiensi    : {eff}%"
        )
        if k < len(riwayat):
            baris.append("─────────────────────────")

    # Simulasi terbaik (total prioritas tertinggi)
    best = max(riwayat, key=lambda x: x["total_prioritas"])
    baris += [
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏆 *Simulasi terbaik*: Budget {rp(best['budget'])} "
        f"→ Prioritas total *{best['total_prioritas']}*",
    ]

    await update.message.reply_text("\n".join(baris), parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: /reset
# ─────────────────────────────────────────────────────────────────────────────
async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data.pop(uid, None)   # hapus semua data user
    await update.message.reply_text(
        "🔄 *Data berhasil direset!*\n\n"
        "Dataset default 28 barang telah dimuat ulang.\n"
        "Gunakan /start untuk melihat menu.",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  HANDLER: pesan tidak dikenal
# ─────────────────────────────────────────────────────────────────────────────
async def pesan_tidak_dikenal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Perintah tidak dikenal.\n"
        "Ketik /start untuk melihat daftar perintah yang tersedia."
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN — Jalankan Bot
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("🤖 Bot Greedy Belanja mulai berjalan...")

    # Inisiasi aplikasi bot
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler untuk /tambah
    conv_tambah = ConversationHandler(
        entry_points=[CommandHandler("tambah", cmd_tambah_start)],
        states={
            TUNGGU_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_tambah_proses),
                CommandHandler("batal", cmd_batal),
            ]
        },
        fallbacks=[CommandHandler("batal", cmd_batal)],
    )

    # Daftarkan semua handler
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("input",   cmd_input))
    app.add_handler(CommandHandler("daftar",  cmd_daftar))
    app.add_handler(CommandHandler("budget",  cmd_budget))
    app.add_handler(CommandHandler("laporan", cmd_laporan))
    app.add_handler(CommandHandler("reset",   cmd_reset))
    app.add_handler(conv_tambah)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pesan_tidak_dikenal))

    # Mulai polling
    print("✅ Bot aktif. Tekan Ctrl+C untuk menghentikan.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
