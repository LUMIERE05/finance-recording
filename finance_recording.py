import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import mysql.connector
from datetime import date
import configparser

def read_config(filename='config.ini'):
    # Inisialisasi parser konfigurasi
    config = configparser.ConfigParser()
    config.read(filename)

    # Membaca variabel konfigurasi dari file
    try:
        db_config = config['Database']
        DB_HOST = db_config['DB_HOST']
        DB_USER = db_config['DB_USER']
        DB_PASSWORD = db_config['DB_PASSWORD']
        DB_NAME = db_config['DB_NAME']
        return DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
    except KeyError as e:
        print(f"KeyError: {e}")
        return None

class Transaction:
    def __init__(self, uang_masuk, uang_keluar):
        self.uang_masuk = [uang_masuk]
        self.uang_keluar = [uang_keluar]

    def show_info(self, kategori):
        pemasukan = sum(self.uang_masuk)
        pengeluaran = sum(self.uang_keluar)
        total = pemasukan - pengeluaran
        print("Transaksi Untuk {} Adalah:".format(kategori))
        print("\tPemasukan\t: Rp{} \n\tPengeluaran\t: Rp{} \n\tTotal\t\t: Rp{}".format(pemasukan, pengeluaran, total))
        self.save_to_mysql(kategori, pemasukan, pengeluaran)

    def save_to_mysql(self, kategori, pemasukan, pengeluaran):
        # Buat koneksi ke MySQL
        # Contoh penggunaan:
        DB_HOST, DB_USER, DB_PASSWORD, DB_NAME = read_config()
        mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Buat kursor untuk berinteraksi dengan database
        mycursor = mydb.cursor()

        # Simpan data hasil perhitungan ke dalam tabel 'transaksi'
        kategori = kategori
        # Pilih tabel sesuai dengan kategori
        if kategori == "Makanan":
            table_name = "transaksi_makanan"
        elif kategori == "Hiburan":
            table_name = "transaksi_hiburan"
        elif kategori == "Transportasi":
            table_name = "transaksi_transportasi"
        elif kategori == "Tabungan":
            table_name = "transaksi_tabungan"
        # Mendapatkan tanggal saat ini
        tanggal_transaksi = date.today()

        # Simpan data transaksi ke tabel yang sesuai
        insert_data = f"INSERT INTO {table_name} (uang_masuk, uang_keluar, tanggal) VALUES (%s, %s, %s)"
        mycursor.execute(insert_data, (pemasukan, pengeluaran, tanggal_transaksi))

        # Simpan perubahan ke database
        mydb.commit()

        # Tutup kursor dan koneksi
        mycursor.close()
        mydb.close()

class Kategori(Transaction):
    def __init__(self, uang_masuk, uang_keluar, kategori):
        super().__init__(uang_masuk, uang_keluar)
        self.kategori = kategori

    def show_info(self):
        super().show_info(self.kategori)

def on_button_click():
    kat = 0
    selected_category = category_var.get()
    pemasukan_text.config(state='normal')
    pengeluaran_text.config(state='normal')

    if selected_category == "Makanan":
        kat = 0
    elif selected_category == "Hiburan":
        kat = 1
    elif selected_category == "Transportasi":
        kat = 2
    elif selected_category == "Tabungan":
        kat = 3

    print(int(entry_1.get()), int(entry_2.get()), category_var.get(), kat)

    pemasukan_text.insert('end', f"Pemasukan ({selected_category}): Rp{entry_1.get()}\n")
    pengeluaran_text.insert('end', f"Pengeluaran ({selected_category}): Rp{entry_2.get()}\n")
    keuangan = Kategori(int(entry_1.get()), int(entry_2.get()), categories[kat])
    keuangan.show_info()

    pemasukan_text.config(state='disabled')
    pengeluaran_text.config(state='disabled')

# Inisialisasi jendela utama
root = tk.Tk()
root.title("Pencatatan Keuangan")

# Mengubah ukuran logo dengan Pillow
original_image = Image.open("logo")  # Ganti dengan path gambar Anda
resized_image = original_image.resize((261, 200), Image.ANTIALIAS)  # Ganti dengan ukuran yang diinginkan
logo_image = ImageTk.PhotoImage(resized_image)

# Menambahkan gambar/logo
logo_label = tk.Label(root, image=logo_image)
logo_label.grid(row=0, column=3, rowspan=3, padx=10)

# Membuat widget
label_1 = tk.Label(root, text="Pemasukan")
entry_1 = tk.Entry(root)
label_2 = tk.Label(root, text="Pengeluaran")
entry_2 = tk.Entry(root)

# Menambahkan pilihan kategori
label_category = tk.Label(root, text="Pilih Kategori:")
categories = ["Makanan", "Hiburan", "Transportasi", "Tabungan"]
category_var = tk.StringVar()
category_var.set(categories[0])
option_menu = tk.OptionMenu(root, category_var, *categories)

button_submit = tk.Button(root, text="Submit", command=on_button_click)

pemasukan_text = tk.Text(root, height=5, width=30, state='disabled')
pengeluaran_text = tk.Text(root, height=5, width=30, state='disabled')

# Menetapkan tata letak dengan grid
label_1.grid(row=0, column=0, pady=10)
entry_1.grid(row=0, column=1, pady=10)
label_2.grid(row=1, column=0, pady=10)
entry_2.grid(row=1, column=1, pady=10)
label_category.grid(row=2, column=0, pady=10)
option_menu.grid(row=2, column=1, pady=10)
button_submit.grid(row=3, column=0, columnspan=2, pady=10)
pemasukan_text.grid(row=4, column=0, columnspan=2, pady=10)
pengeluaran_text.grid(row=4, column=3, columnspan=2, pady=10)

# Menjalankan loop utama
root.mainloop()
