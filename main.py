import telebot
import sqlite3
import pandas as pd

TOKEN = "HTTP API:
8346747984:AAFJsczHIEbhoKDG4pWMHcJKl-wrbnewYLY"
ADMIN_ID = @tomifrh   # ganti dengan id telegram kamu

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("shop.db",check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
customer TEXT,
barang TEXT,
harga INTEGER,
resi TEXT,
tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pengeluaran(
id INTEGER PRIMARY KEY AUTOINCREMENT,
jumlah INTEGER,
keterangan TEXT,
tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

db.commit()


def is_admin(m):
    return m.from_user.id == ADMIN_ID


@bot.message_handler(commands=['start'])
def start(m):

    if not is_admin(m):
        return

    bot.reply_to(m,
"""
Halo bre 👋
KasirAnomali Disini
BOT ONLINE SHOP MODE DEWA

Contoh chat:
budi hoodie hitam 85000
keluar 20000 beli plastik
resi 1 JNT123456
laporan
export
""")


@bot.message_handler(func=lambda m: True)
def auto_handler(m):

    if not is_admin(m):
        return

    text = m.text.lower()

    if text.startswith("keluar"):

        data = m.text.split(" ",2)
        jumlah = int(data[1])
        ket = data[2]

        cursor.execute(
        "INSERT INTO pengeluaran(jumlah,keterangan) VALUES(?,?)",
        (jumlah,ket))

        db.commit()

        bot.reply_to(m,"💸 Pengeluaran dicatat bre")
        return


    if text.startswith("resi"):

        data = m.text.split(" ")

        id_order = data[1]
        resi = data[2]

        cursor.execute(
        "UPDATE orders SET resi=? WHERE id=?",
        (resi,id_order))

        db.commit()

        bot.reply_to(m,"📦 Resi berhasil ditambah")
        return


    if text == "laporan":

        cursor.execute("SELECT COUNT(*) FROM orders")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(harga) FROM orders")
        omzet = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(jumlah) FROM pengeluaran")
        keluar = cursor.fetchone()[0] or 0

        profit = omzet - keluar

        cursor.execute("""
        SELECT barang,COUNT(*)
        FROM orders
        GROUP BY barang
        ORDER BY COUNT(*) DESC
        LIMIT 3
        """)

        top = cursor.fetchall()

        msg = f"""
📊 Laporan

Order: {total}
Omset: {omzet}
Pengeluaran: {keluar}
Profit: {profit}

Produk Terlaris:
"""

        for i,x in enumerate(top,1):
            msg += f"{i}. {x[0]} - {x[1]}\n"

        bot.reply_to(m,msg)
        return


    if text == "export":

        df = pd.read_sql_query("SELECT * FROM orders",db)

        file = "orders.xlsx"
        df.to_excel(file,index=False)

        bot.send_document(m.chat.id,open(file,"rb"))
        return


    parts = m.text.split(" ")

    if parts[-1].isdigit():

        harga = int(parts[-1])
        customer = parts[0]
        barang = " ".join(parts[1:-1])

        cursor.execute(
        "INSERT INTO orders(customer,barang,harga) VALUES(?,?,?)",
        (customer,barang,harga))

        db.commit()

        bot.reply_to(m,"🔥 Order dicatat bre")
        return


    bot.reply_to(m,"Anjir gw ga ngerti bre 😭")


bot.infinity_polling()
