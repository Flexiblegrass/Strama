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
    /input           → Input barang baru dari nol
    /tambah          → Tambah barang ke daftar yang sudah ada
    /daftar          → Lihat semua barang user
    /budget 100000   → Jalankan algoritma greedy
    /hapus <nomor>   → Hapus satu/banyak barang dari daftar
    /edit <nomor>    → Edit nama/harga/prioritas barang
    /laporan         → Riwayat semua simulasi
    /reset           → Hapus semua data user & mulai dari awal

  Instalasi:
    pip install python-telegram-bot

  Cara pakai:
    1. Buat bot lewat @BotFather di Telegram → copy token
    2. Tempel token ke variabel BOT_TOKEN di bawah
    3. Jalankan: python bot_greedy_constraint.py
===========================================================================
"""

import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

#  KONFIGURASI BOT
BOT_TOKEN = "MASUKKAN_TOKEN_BOT_DISINI"   

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TUNGGU_INPUT, TUNGGU_EDIT = range(2)


user_store: dict[int, dict] = {}


def get_user(user_id: int) -> dict:
    if user_id not in user_store:
        user_store[user_id] = {
            "barang":  [],
            "riwayat": [],
        }
    return user_store[user_id]

#  ALGORITMA GREEDY 2 TAHAP

def algoritma_greedy_constraint(items: list, budget: int) -> tuple:
    """
    Algoritma Greedy dengan Constraint Prioritas (2 Tahap).
    Tahap 1 – WAJIB: prioritas ≥ 9, diurutkan termurah dulu.
    Tahap 2 – GREEDY: rasio = prioritas / harga, descending.
    """
    selected      = []
    sisa_budget   = budget
    terpilih_nama = set()

    # TAHAP 1: WAJIB 
    barang_wajib = sorted(
        [item for item in items if item["prioritas"] >= 9],
        key=lambda x: x["harga"]
    )
    for item in barang_wajib:
        if sisa_budget >= item["harga"]:
            dipilih = dict(item)
            dipilih["tahap"] = "Wajib"
            selected.append(dipilih)
            terpilih_nama.add(item["nama_barang"])
            sisa_budget -= item["harga"]

    # TAHAP 2: GREEDY 
    sisa_barang = [item for item in items if item["nama_barang"] not in terpilih_nama]
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

def rp(nominal: int) -> str:
    return f"Rp {nominal:,}".replace(",", ".")

def rp_v2(nominal: int) -> str:
    return f"Rp {nominal:,}".replace(",", "\\.")

def escape_v2(teks: str) -> str:
    reserved = r"\_*[]()~`>#+-=|{}.!"
    for ch in reserved:
        teks = teks.replace(ch, f"\\{ch}")
    return teks


def parse_input_barang(teks: str) -> dict | None:
    token = teks.strip().split()
    if not token:
        return None

    if len(token) >= 3 and token[0].isdigit():
        try:
            prioritas   = int(token[0])
            nama_barang = " ".join(token[1:-1])
            harga       = int(token[-1])
            if 1 <= prioritas <= 10 and harga > 0 and nama_barang:
                return {"nama_barang": nama_barang, "harga": harga,
                        "prioritas": prioritas, "kategori": "Lainnya"}
        except ValueError:
            pass

    if "prioritas" in token:
        try:
            idx_p       = token.index("prioritas")
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

    if len(token) >= 3:
        try:
            harga       = int(token[-2])
            prioritas   = int(token[-1])
            nama_barang = " ".join(token[:-2])
            if 1 <= prioritas <= 10 and harga > 0 and nama_barang:
                return {"nama_barang": nama_barang, "harga": harga,
                        "prioritas": prioritas, "kategori": "Lainnya"}
        except ValueError:
            pass

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


def parse_multiline_input(teks: str) -> tuple[list, list]:
    berhasil = []
    gagal    = []
    for baris in teks.strip().splitlines():
        baris = baris.strip()
        if not baris:
            continue
        item = parse_input_barang(baris)
        if item:
            berhasil.append(item)
        else:
            gagal.append(baris)
    return berhasil, gagal

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ud   = get_user(user.id)

    pesan = (
        f"👋 Halo, *{escape_v2(user.first_name)}*\\!\n\n"
        "🛒 *Sistem Optimasi Belanja — Algoritma Greedy*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Bot ini memilih barang belanjaan secara *cerdas* menggunakan "
        "*Algoritma Greedy 2 Tahap*:\n\n"
        "🔴 *Tahap 1 – WAJIB*\n"
        "    Barang prioritas ≥ 9 dipilih lebih dulu\n"
        "    \\(beras, air, gas, telur, dll\\)\n\n"
        "🟢 *Tahap 2 – GREEDY*\n"
        "    Sisa budget dioptimalkan berdasarkan\n"
        "    rasio Prioritas / Harga tertinggi\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Daftar Perintah:*\n"
        "▸ /start — Menu ini\n"
        "▸ /input — Input barang baru dari nol\n"
        "▸ /tambah — Tambah barang ke daftar yang ada\n"
        "▸ /daftar — Lihat semua barang\n"
        "▸ /budget `<nominal>` — Hitung rekomendasi belanja\n"
        "    contoh: `/budget 100000`\n"
        "▸ /hapus `<nomor>` — Hapus satu/banyak barang\n"
        "▸ /edit `<nomor>` — Edit nama/harga/prioritas barang\n"
        "▸ /laporan — Riwayat semua simulasi\n"
        "▸ /reset — Hapus data & mulai ulang\n\n"
        f"📦 Total barang saat ini: *{len(ud['barang'])} barang*\n"
        "Mulai dengan /input atau /tambah untuk menambah barang\\!"
    )
    await update.message.reply_text(pesan, parse_mode="MarkdownV2")

async def cmd_input_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)

    ud["barang"] = []

    await update.message.reply_text(
        "📝 *Input Barang Baru*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Daftar barang sebelumnya telah dikosongkan\\.\n\n"
        "Kirim barang kamu, satu atau *banyak sekaligus* \\(satu baris per barang\\)\\.\n\n"
        "Format:\n"
        "```\nnama harga prioritas\nContoh: sabun 15000 9\n```\n\n"
        "📌 *Skala Prioritas:*\n"
        "🔴 `9–10` \\= Kebutuhan utama/pokok\n"
        "🟡 `6–8`  \\= Kebutuhan penting\n"
        "🟢 `1–5`  \\= Kebutuhan tambahan\n\n"
        "Ketik /selesai jika sudah selesai input barang\\.",
        parse_mode="MarkdownV2",
    )
    return TUNGGU_INPUT


async def cmd_input_selesai_lalu_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    ud    = get_user(uid)
    items = ud["barang"]

    if not items:
        await update.message.reply_text(
            "⚠️ Belum ada barang yang diinput\\.\n"
            "Kirim minimal satu barang dulu\\.",
            parse_mode="MarkdownV2",
        )
        return TUNGGU_INPUT

    await update.message.reply_text(
        f"✅ *{len(items)} barang tersimpan\\!*\n\n"
        f"Gunakan `/budget <nominal>` untuk mendapat rekomendasi belanja\\.\n"
        f"Contoh: `/budget 100000`\n\n"
        f"Atau ketik /start untuk kembali ke menu utama\\.",
        parse_mode="MarkdownV2",
    )
    return ConversationHandler.END

# INPUT BARANG 
async def cmd_input_barang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.strip()
    uid  = update.effective_user.id
    ud   = get_user(uid)

    berhasil, gagal = parse_multiline_input(teks)

    if not berhasil and not gagal:
        await update.message.reply_text(
            "❌ Pesan kosong\\. Kirim data barang dalam format:\n"
            "`nama harga prioritas`",
            parse_mode="MarkdownV2",
        )
        return TUNGGU_INPUT

    for item in berhasil:
        ud["barang"].append(item)

    baris_resp = []

    if berhasil:
        baris_resp.append(f"✅ *{len(berhasil)} barang ditambahkan\\!*\n")
        for item in berhasil:
            p = item["prioritas"]
            if   p >= 9: level = "🔴 Utama"
            elif p >= 6: level = "🟡 Penting"
            else:        level = "🟢 Tambahan"
            catatan = " ⚠️ _\\(prioritas default 5\\)_" if item.get("_default_prioritas") else ""
            baris_resp.append(
                f"  📦 *{escape_v2(item['nama_barang'])}*\n"
                f"     💰 {rp_v2(item['harga'])}  \\|  ⭐ {p}/10  {level}{catatan}"
            )

    if gagal:
        baris_resp.append(f"\n❌ *{len(gagal)} baris tidak dikenali:*")
        for b in gagal:
            baris_resp.append(f"  `{b}`")
        baris_resp.append(
            "\n_Format yang benar: `nama harga prioritas`_\n"
            "_Contoh: `sabun 15000 9`_"
        )

    baris_resp.append(f"\n📊 Total barang dalam daftar: *{len(ud['barang'])}*")
    await update.message.reply_text("\n".join(baris_resp), parse_mode="MarkdownV2")

    items  = ud["barang"]
    daftar = ["📋 *Daftar barang kamu sekarang:*\n"]
    for i, item in enumerate(items, 1):
        if   item["prioritas"] >= 9: ikon = "🔴"
        elif item["prioritas"] >= 6: ikon = "🟡"
        else:                        ikon = "🟢"
        daftar.append(
            f"{i}\\. {ikon} *{escape_v2(item['nama_barang'])}*\n"
            f"    💰 {rp_v2(item['harga'])}  \\|  ⭐ {item['prioritas']}"
        )
    daftar.append(
        "\nLanjut input, atau:\n"
        "/selesai → Tutup sesi input\n"
        "/batal   → Batalkan"
    )

    teks_daftar = "\n".join(daftar)
    if len(teks_daftar) <= 4000:
        await update.message.reply_text(teks_daftar, parse_mode="MarkdownV2")
    else:
        mid = len(items) // 2
        await update.message.reply_text("\n".join(daftar[:2 + mid]), parse_mode="MarkdownV2")
        await update.message.reply_text("\n".join(daftar[2 + mid:]), parse_mode="MarkdownV2")

    return TUNGGU_INPUT


async def cmd_input_selesai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)
    await update.message.reply_text(
        f"✅ *Sesi input selesai\\.*\n"
        f"Total barang dalam daftar: *{len(ud['barang'])}*\n\n"
        "Ketik /start untuk kembali ke menu utama\\.",
        parse_mode="MarkdownV2",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cmd_batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❎ Sesi input dibatalkan\\.\nKetik /start untuk kembali ke menu utama\\.",
        parse_mode="MarkdownV2",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def cmd_tambah_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ *Tambah Barang*\n\n"
        "Kirim data barang dalam format:\n"
        "`nama harga prioritas`\n\n"
        "Boleh *banyak sekaligus* \\(satu baris per barang\\)\\:\n"
        "```\nIndomie Goreng 3500 4\n9 Beras 5kg 72000\nSusu 17000 prioritas 5\n```\n\n"
        "Ketik /selesai jika sudah, atau /batal untuk membatalkan\\.",
        parse_mode="MarkdownV2",
    )
    return TUNGGU_INPUT

async def cmd_daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    ud    = get_user(uid)
    items = ud["barang"]

    if not items:
        await update.message.reply_text(
            "📭 Daftar barang kosong\\.\nGunakan /tambah atau /input untuk menambah barang\\.",
            parse_mode="MarkdownV2",
        )
        return

    n_utama    = sum(1 for i in items if i["prioritas"] >= 9)
    n_penting  = sum(1 for i in items if 6 <= i["prioritas"] <= 8)
    n_tambahan = sum(1 for i in items if i["prioritas"] <= 5)

    baris = [
        f"📋 *Daftar Barang* \\({len(items)} item\\)",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🔴 Utama: {n_utama}  \\|  🟡 Penting: {n_penting}  \\|  🟢 Tambahan: {n_tambahan}",
        "────────────────────────",
    ]

    for i, item in enumerate(items, 1):
        if   item["prioritas"] >= 9: ikon = "🔴"
        elif item["prioritas"] >= 6: ikon = "🟡"
        else:                        ikon = "🟢"
        baris.append(
            f"{i:>2}\\. {ikon} *{escape_v2(item['nama_barang'])}*\n"
            f"    💰 {rp_v2(item['harga'])}  \\|  ⭐ Prioritas: {item['prioritas']}"
        )

    teks = "\n".join(baris)
    if len(teks) <= 4000:
        await update.message.reply_text(teks, parse_mode="MarkdownV2")
    else:
        mid = len(items) // 2
        await update.message.reply_text("\n".join(baris[:4 + mid]), parse_mode="MarkdownV2")
        await update.message.reply_text("\n".join(baris[4 + mid:]), parse_mode="MarkdownV2")

async def cmd_hapus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    ud    = get_user(uid)
    items = ud["barang"]

    if not context.args:
        if not items:
            await update.message.reply_text("📭 Daftar barang kosong.")
            return
        baris = ["🗑 *Hapus Barang*\n\nKetik `/hapus <nomor>` untuk menghapus\\.\nBoleh banyak: `/hapus 2 3 4` atau `/hapus 2, 3, 4`\n\nDaftar barang:"]
        for i, item in enumerate(items, 1):
            if   item["prioritas"] >= 9: ikon = "🔴"
            elif item["prioritas"] >= 6: ikon = "🟡"
            else:                        ikon = "🟢"
            baris.append(
                f"{i}\\. {ikon} *{escape_v2(item['nama_barang'])}* "
                f"— {rp_v2(item['harga'])} \\| ⭐{item['prioritas']}"
            )
        await update.message.reply_text("\n".join(baris), parse_mode="MarkdownV2")
        return

    raw        = " ".join(context.args).replace(",", " ")
    nomor_list = []
    invalid    = []

    for token in raw.split():
        token = token.strip()
        if not token:
            continue
        try:
            n = int(token)
            if 1 <= n <= len(items):
                nomor_list.append(n)
            else:
                invalid.append(token)
        except ValueError:
            invalid.append(token)

    if not nomor_list:
        await update.message.reply_text(
            f"❌ Tidak ada nomor valid\\. Masukkan angka 1–{len(items)}\\.\n"
            f"Ketik `/hapus` untuk melihat daftar\\.",
            parse_mode="MarkdownV2",
        )
        return

    nomor_unik = sorted(set(nomor_list), reverse=True)
    dihapus    = []
    for n in nomor_unik:
        dihapus.append(items[n - 1]["nama_barang"])
        items.pop(n - 1)
    dihapus.reverse()

    baris_resp = [f"✅ *{len(dihapus)} barang berhasil dihapus:*\n"]
    for nama in dihapus:
        baris_resp.append(f"  🗑 {nama}")
    baris_resp.append(f"\nTotal barang tersisa: *{len(items)}*")

    if invalid:
        baris_resp.append(f"\n⚠️ Nomor tidak valid diabaikan: {', '.join(invalid)}")

    await update.message.reply_text("\n".join(baris_resp), parse_mode="Markdown")

async def cmd_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    ud    = get_user(uid)
    items = ud["barang"]

    if not context.args:
        if not items:
            await update.message.reply_text("📭 Daftar barang kosong.")
            return
        baris = ["✏️ *Edit Barang*\n\nKetik `/edit <nomor>` untuk mengedit\\.\n\nDaftar barang:"]
        for i, item in enumerate(items, 1):
            if   item["prioritas"] >= 9: ikon = "🔴"
            elif item["prioritas"] >= 6: ikon = "🟡"
            else:                        ikon = "🟢"
            baris.append(
                f"{i}\\. {ikon} *{escape_v2(item['nama_barang'])}* "
                f"— {rp_v2(item['harga'])} \\| ⭐{item['prioritas']}"
            )
        await update.message.reply_text("\n".join(baris), parse_mode="MarkdownV2")
        return

    try:
        nomor = int(context.args[0])
        if not (1 <= nomor <= len(items)):
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            f"❌ Nomor tidak valid\\. Masukkan angka 1–{len(items)}\\.\n"
            f"Ketik `/edit` untuk melihat daftar\\.",
            parse_mode="MarkdownV2",
        )
        return

    context.user_data["edit_index"] = nomor - 1
    item = items[nomor - 1]

    await update.message.reply_text(
        f"✏️ *Edit Barang \\#{nomor}*\n\n"
        f"Data saat ini:\n"
        f"📦 Nama      : *{escape_v2(item['nama_barang'])}*\n"
        f"💰 Harga     : *{rp_v2(item['harga'])}*\n"
        f"⭐ Prioritas : *{item['prioritas']}/10*\n\n"
        f"Kirim data baru dengan format:\n"
        f"`nama baru | harga baru | prioritas baru`\n\n"
        f"Gunakan `-` untuk bagian yang tidak ingin diubah:\n"
        f"`\\- | 20000 | \\-` → hanya ubah harga\n\n"
        f"Ketik /batal untuk membatalkan\\.",
        parse_mode="MarkdownV2",
    )
    return TUNGGU_EDIT


async def cmd_edit_proses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    ud    = get_user(uid)
    items = ud["barang"]
    idx   = context.user_data.get("edit_index")

    if idx is None or idx >= len(items):
        await update.message.reply_text(
            "❌ Sesi edit tidak valid\\. Mulai ulang dengan /edit\\.",
            parse_mode="MarkdownV2",
        )
        return ConversationHandler.END

    teks   = update.message.text.strip()
    bagian = [b.strip() for b in teks.split("|")]

    if len(bagian) != 3:
        await update.message.reply_text(
            "❌ Format salah\\. Gunakan:\n"
            "`nama baru | harga baru | prioritas baru`\n\n"
            "Pakai `-` untuk bagian yang tidak ingin diubah\\.\n"
            "Coba lagi atau /batal\\.",
            parse_mode="MarkdownV2",
        )
        return TUNGGU_EDIT

    item      = items[idx]
    nama_lama = item["nama_barang"]
    perubahan = []

    if bagian[0] not in ("-", ""):
        item["nama_barang"] = bagian[0]
        perubahan.append(f"📦 Nama      : {nama_lama} → *{item['nama_barang']}*")

    if bagian[1] not in ("-", ""):
        try:
            harga_baru = int(bagian[1].replace(".", "").replace(",", ""))
            if harga_baru <= 0:
                raise ValueError
            harga_lama = item["harga"]
            item["harga"] = harga_baru
            perubahan.append(f"💰 Harga     : {rp(harga_lama)} → *{rp(harga_baru)}*")
        except ValueError:
            await update.message.reply_text(
                "❌ Harga tidak valid\\. Masukkan angka positif\\.\nCoba lagi atau /batal\\.",
                parse_mode="MarkdownV2",
            )
            return TUNGGU_EDIT

    if bagian[2] not in ("-", ""):
        try:
            prior_baru = int(bagian[2])
            if not (1 <= prior_baru <= 10):
                raise ValueError
            prior_lama = item["prioritas"]
            item["prioritas"] = prior_baru
            perubahan.append(f"⭐ Prioritas : {prior_lama} → *{prior_baru}/10*")
        except ValueError:
            await update.message.reply_text(
                "❌ Prioritas tidak valid\\. Masukkan angka 1–10\\.\nCoba lagi atau /batal\\.",
                parse_mode="MarkdownV2",
            )
            return TUNGGU_EDIT

    if not perubahan:
        await update.message.reply_text(
            "⚠️ Tidak ada yang diubah \\(semua diisi `-`\\)\\.",
            parse_mode="MarkdownV2",
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "✅ *Barang berhasil diperbarui\\!*\n\n" + "\n".join(perubahan),
        parse_mode="MarkdownV2",
    )
    return ConversationHandler.END

# BUDGET 
async def cmd_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ud  = get_user(uid)

    if not context.args or not context.args[0].replace(".", "").replace(",", "").isdigit():
        await update.message.reply_text(
            "⚠️ Format: `/budget <nominal>`\nContoh: `/budget 100000`",
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
            "📭 Daftar barang kosong.\nGunakan /input atau /tambah untuk menambah barang."
        )
        return

    selected, total = algoritma_greedy_constraint(items, budget)
    total_pri = sum(i["prioritas"] for i in selected)
    sisa      = budget - total
    n_wajib   = sum(1 for i in selected if i["tahap"] == "Wajib")
    n_greedy  = sum(1 for i in selected if i["tahap"] == "Greedy")

    ud["riwayat"].append({
        "budget":          budget,
        "jumlah_item":     len(selected),
        "n_wajib":         n_wajib,
        "n_greedy":        n_greedy,
        "total_biaya":     total,
        "total_prioritas": total_pri,
        "sisa_budget":     sisa,
        "barang_terpilih": [i["nama_barang"] for i in selected],
    })

    baris = [
        "🛒 *Rekomendasi Belanja — Algoritma Greedy*",
        f"💰 Budget  : *{rp(budget)}*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if not selected:
        baris.append("😔 Tidak ada barang yang dapat dibeli dengan budget ini.")
    else:
        if n_wajib > 0:
            baris.append("🔴 *TAHAP 1 — PRIORITAS WAJIB (≥9)*")
            for j, item in enumerate([i for i in selected if i["tahap"] == "Wajib"], 1):
                baris.append(
                    f"  {j}. *{item['nama_barang']}*\n"
                    f"     💰 {rp(item['harga'])}  |  ⭐ {item['prioritas']}"
                )
        if n_greedy > 0:
            baris.append("🟢 *TAHAP 2 — GREEDY (Rasio P/H)*")
            for j, item in enumerate([i for i in selected if i["tahap"] == "Greedy"], 1):
                rasio = round(item.get("rasio", item["prioritas"] / item["harga"]) * 1000, 2)
                baris.append(
                    f"  {j}. *{item['nama_barang']}*\n"
                    f"     💰 {rp(item['harga'])}  |  ⭐ {item['prioritas']}  |  📊 {rasio:.2f}"
                )
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
    if len(teks) <= 4000:
        await update.message.reply_text(teks, parse_mode="Markdown")
    else:
        mid = len(selected) // 2
        await update.message.reply_text("\n".join(baris[:6 + n_wajib + 1]), parse_mode="Markdown")
        await update.message.reply_text("\n".join(baris[6 + n_wajib + 1:]), parse_mode="Markdown")

    await update.message.reply_text(
        "Ketik /start untuk kembali ke menu utama\\.",
        parse_mode="MarkdownV2",
    )

# LAPORAN
async def cmd_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid     = update.effective_user.id
    ud      = get_user(uid)
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
        f"Total simulasi   : *{len(riwayat)}x*",
        f"Total pengeluaran: *{rp(total_pengeluaran)}*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    for k, r in enumerate(riwayat, 1):
        eff = round(r["total_biaya"] / r["budget"] * 100, 1)
        baris.append(
            f"*Simulasi {k}*\n"
            f"  💰 Budget     : {rp(r['budget'])}\n"
            f"  📦 Item       : {r['jumlah_item']} ({r['n_wajib']} wajib + {r['n_greedy']} greedy)\n"
            f"  💳 Biaya      : {rp(r['total_biaya'])}\n"
            f"  ⭐ Prioritas  : {r['total_prioritas']}\n"
            f"  💵 Sisa       : {rp(r['sisa_budget'])}\n"
            f"  📈 Efisiensi  : {eff}%"
        )
        if k < len(riwayat):
            baris.append("────────────────────────")

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

# RESET DATA 
async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_store.pop(uid, None)
    context.user_data.clear()

    await update.message.reply_text(
        "🔄 *Data berhasil direset\\!*\n\n"
        "Semua data barang dan riwayat simulasi telah dihapus\\.\n"
        "Ketik /start untuk kembali ke menu utama\\.",
        parse_mode="MarkdownV2",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def pesan_tidak_dikenal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Perintah tidak dikenali.\n"
        "Ketik /start untuk melihat semua perintah yang tersedia."
    )

def main():
    print("🤖 Bot Greedy Constraint mulai berjalan...")
    print("   Tekan Ctrl+C untuk menghentikan.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    # ── /input: input barang baru dari nol → /selesai → pakai /budget ──
    conv_input = ConversationHandler(
        entry_points=[CommandHandler("input", cmd_input_start)],
        states={
            TUNGGU_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_input_barang),
                CommandHandler("selesai", cmd_input_selesai_lalu_budget),
                CommandHandler("batal",   cmd_batal),
                CommandHandler("reset",   cmd_reset),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cmd_batal),
            CommandHandler("reset", cmd_reset),
        ],
    )

    # ── /tambah: tambah ke daftar yang sudah ada ──
    conv_tambah = ConversationHandler(
        entry_points=[CommandHandler("tambah", cmd_tambah_start)],
        states={
            TUNGGU_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_input_barang),
                CommandHandler("selesai", cmd_input_selesai),
                CommandHandler("batal",   cmd_batal),
                CommandHandler("reset",   cmd_reset),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cmd_batal),
            CommandHandler("reset", cmd_reset),
        ],
    )

    # ── /edit ──
    conv_edit = ConversationHandler(
        entry_points=[CommandHandler("edit", cmd_edit_start)],
        states={
            TUNGGU_EDIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_edit_proses),
                CommandHandler("batal", cmd_batal),
                CommandHandler("reset", cmd_reset),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cmd_batal),
            CommandHandler("reset", cmd_reset),
        ],
    )

    # ── Daftarkan semua handler ──
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("daftar",  cmd_daftar))
    app.add_handler(CommandHandler("budget",  cmd_budget))
    app.add_handler(CommandHandler("hapus",   cmd_hapus))
    app.add_handler(CommandHandler("laporan", cmd_laporan))
    app.add_handler(CommandHandler("reset",   cmd_reset))
    app.add_handler(conv_input)
    app.add_handler(conv_tambah)
    app.add_handler(conv_edit)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, pesan_tidak_dikenal)
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()