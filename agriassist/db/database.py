import sqlite3
import os

DB_PATH = "agriassist.db"


def init_db():
    """Buat tabel dan isi data awal jika belum ada."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS pupuk (
            pupuk_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pupuk VARCHAR(255) NOT NULL,
            harga      INTEGER NOT NULL,
            fungsi     TEXT
        );

        CREATE TABLE IF NOT EXISTS obat_pertanian (
            obat_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_obat  VARCHAR(255) NOT NULL,
            kategori   VARCHAR(100) NOT NULL,
            harga      INTEGER NOT NULL,
            kegunaan   TEXT
        );

        CREATE TABLE IF NOT EXISTS hama_penyakit (
            hama_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_hama    VARCHAR(255) NOT NULL,
            gejala       TEXT,
            penanganan   TEXT
        );
        """)

        # Seed data hanya jika tabel masih kosong
        cur.execute("SELECT COUNT(*) FROM pupuk")
        if cur.fetchone()[0] == 0:
            cur.executescript("""
            INSERT INTO pupuk (nama_pupuk, harga, fungsi) VALUES
                ('Urea',        120000, 'Memacu pertumbuhan daun dan batang'),
                ('NPK Phonska', 145000, 'Meningkatkan pertumbuhan dan hasil panen'),
                ('ZA',           95000, 'Menambah unsur nitrogen dan sulfur'),
                ('KCl',         170000, 'Meningkatkan kualitas buah dan ketahanan tanaman');

            INSERT INTO obat_pertanian (nama_obat, kategori, harga, kegunaan) VALUES
                ('Decis',    'Insektisida', 55000, 'Mengendalikan hama wereng'),
                ('Curacron', 'Insektisida', 85000, 'Mengendalikan ulat dan serangga'),
                ('Score',    'Fungisida',   75000, 'Mengendalikan penyakit blas'),
                ('Antracol', 'Fungisida',   68000, 'Mengendalikan penyakit akibat jamur');

            INSERT INTO hama_penyakit (nama_hama, gejala, penanganan) VALUES
                ('Wereng Coklat',  'Daun menguning dan tanaman layu',          'Gunakan varietas tahan dan insektisida sesuai dosis'),
                ('Penyakit Blas',  'Bercak berbentuk belah ketupat pada daun', 'Gunakan fungisida dan atur kelembapan lahan'),
                ('Ulat Grayak',    'Daun berlubang dan habis dimakan',          'Pengendalian mekanis atau insektisida');
            """)
        conn.commit()


def list_tables() -> list:
    """Menampilkan semua tabel yang tersedia di database."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cur.fetchall()]


def describe_table(table_name: str) -> list:
    """Menampilkan struktur kolom dari suatu tabel."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name})")
        return [(col[1], col[2]) for col in cur.fetchall()]


def execute_query(sql: str) -> list:
    """Menjalankan query SELECT pada database."""
    # Keamanan dasar: hanya izinkan SELECT
    if not sql.strip().upper().startswith("SELECT"):
        return [("Error", "Hanya query SELECT yang diizinkan.")]
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
