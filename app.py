from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from ml_model import prediksi

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'spk_pkl'

mysql = MySQL(app)

# ================== HOME ==================
@app.route('/')
def home():
    return render_template('index.html')


# ================== TAMBAH DATA ==================
@app.route('/tempat_pkl', methods=['GET', 'POST'])
def tempat_pkl():
    if request.method == 'POST':
        nama_pkl = request.form['nama_pkl']
        jurusan = request.form['jurusan']  # ✅ TAMBAHAN
        lokasi_pkl = request.form['lokasi_pkl']
        jarak = request.form['jarak']
        fasilitas = request.form['fasilitas']
        reputasi = request.form['reputasi']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO tempat_pkl 
            (nama_pkl, jurusan, lokasi_pkl, jarak, fasilitas, reputasi)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nama_pkl, jurusan, lokasi_pkl, jarak, fasilitas, reputasi))
        mysql.connection.commit()
        cur.close()

        return redirect('/list_tempat_pkl')

    return render_template('tempat_pkl.html')


# ================== LIST DATA ==================
@app.route('/list_tempat_pkl')
def list_tempat_pkl():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tempat_pkl")
    data = cur.fetchall()
    cur.close()

    return render_template('list_tempat_pkl.html', data=data)


# ================== EDIT DATA ==================
@app.route('/edit_tempat_pkl/<int:id>', methods=['GET', 'POST'])
def edit_tempat_pkl(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama_pkl = request.form['nama_pkl']
        jurusan = request.form['jurusan']  # ✅ TAMBAHAN
        lokasi_pkl = request.form['lokasi_pkl']
        jarak = request.form['jarak']
        fasilitas = request.form['fasilitas']
        reputasi = request.form['reputasi']

        cur.execute("""
            UPDATE tempat_pkl
            SET nama_pkl=%s, jurusan=%s, lokasi_pkl=%s, jarak=%s, fasilitas=%s, reputasi=%s
            WHERE id_pkl=%s
        """, (nama_pkl, jurusan, lokasi_pkl, jarak, fasilitas, reputasi, id))

        mysql.connection.commit()
        cur.close()

        return redirect('/list_tempat_pkl')

    cur.execute("SELECT * FROM tempat_pkl WHERE id_pkl = %s", (id,))
    data = cur.fetchone()
    cur.close()

    return render_template('edit_tempat_pkl.html', data=data)


# ================== HAPUS ==================
@app.route('/hapus_tempat_pkl/<int:id>')
def hapus_tempat_pkl(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tempat_pkl WHERE id_pkl = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect('/list_tempat_pkl')


# ================== HASIL SAW ==================
@app.route('/hasil')
def hasil():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_pkl, nama_pkl, jurusan, lokasi_pkl, jarak, fasilitas, reputasi FROM tempat_pkl")
    data = cur.fetchall()

    hasil_perhitungan = []

    for row in data:
        nama_pkl = row[1]
        lokasi = row[3]
        jarak = row[4]
        fasilitas = row[5]
        reputasi = row[6]

        # konversi nilai
        nilai_jarak = 3 if jarak == 'Dekat' else 2 if jarak == 'Sedang' else 1
        nilai_fasilitas = 3 if fasilitas == 'Lengkap' else 2 if fasilitas == 'Cukup' else 1
        nilai_reputasi = 3 if reputasi == 'Sangat Baik' else 2 if reputasi == 'Baik' else 1

        # SAW
        nilai_akhir = (
            (nilai_jarak * 0.2) +
            (nilai_fasilitas * 0.3) +
            (nilai_reputasi * 0.5)
        ) / 3

        hasil_perhitungan.append({
            'nama_pkl': nama_pkl,
            'lokasi': lokasi,
            'nilai': round(nilai_akhir, 3)
        })

    hasil_perhitungan = sorted(hasil_perhitungan, key=lambda x: x['nilai'], reverse=True)

    cur.close()
    return render_template('hasil.html', hasil=hasil_perhitungan)

# ================== KRITERIA ==================
@app.route('/kriteria')
def kriteria():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kriteria")
    data_kriteria = cur.fetchall()
    cur.close()

    return render_template('kriteria.html', kriteria=data_kriteria)


# ================== PENILAIAN ==================
@app.route('/penilaian')
def penilaian():
    data_penilaian = [
        {'kriteria': 'Jarak', 'keterangan': 'Dekat', 'nilai': 3},
        {'kriteria': 'Jarak', 'keterangan': 'Sedang', 'nilai': 2},
        {'kriteria': 'Jarak', 'keterangan': 'Jauh', 'nilai': 1},

        {'kriteria': 'Fasilitas', 'keterangan': 'Lengkap', 'nilai': 3},
        {'kriteria': 'Fasilitas', 'keterangan': 'Cukup', 'nilai': 2},
        {'kriteria': 'Fasilitas', 'keterangan': 'Kurang', 'nilai': 1},

        {'kriteria': 'Reputasi', 'keterangan': 'Sangat Baik', 'nilai': 3},
        {'kriteria': 'Reputasi', 'keterangan': 'Baik', 'nilai': 2},
        {'kriteria': 'Reputasi', 'keterangan': 'Cukup', 'nilai': 1},
    ]

    return render_template('penilaian.html', penilaian=data_penilaian)


# ================== EVALUASI ==================
@app.route('/evaluasi')
def evaluasi():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM tempat_pkl")
    total_pkl = cur.fetchone()[0]

    cur.execute("SELECT jarak, COUNT(*) FROM tempat_pkl GROUP BY jarak")
    data_jarak = cur.fetchall()

    cur.execute("SELECT fasilitas, COUNT(*) FROM tempat_pkl GROUP BY fasilitas")
    data_fasilitas = cur.fetchall()

    cur.execute("SELECT reputasi, COUNT(*) FROM tempat_pkl GROUP BY reputasi")
    data_reputasi = cur.fetchall()

    cur.close()

    return render_template(
        'evaluasi.html',
        total_pkl=total_pkl,
        data_jarak=data_jarak,
        data_fasilitas=data_fasilitas,
        data_reputasi=data_reputasi
    )


# ================== PREDIKSI ML ==================
@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi_pkl():
    if request.method == 'POST':
        jurusan = request.form['jurusan']
        jarak = request.form['jarak']
        fasilitas = request.form['fasilitas']
        reputasi = request.form['reputasi']

        hasil = prediksi(mysql, jurusan, jarak, fasilitas, reputasi)

        return render_template('hasil_prediksi.html', hasil=hasil)

    return render_template('prediksi.html')


# ================== RUN ==================
if __name__ == '__main__':
    app.run(debug=True)