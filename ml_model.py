from sklearn.tree import DecisionTreeClassifier
import pandas as pd

def prediksi(mysql, jurusan, jarak, fasilitas, reputasi):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT jurusan, nama_pkl, jarak, fasilitas, reputasi
        FROM tempat_pkl
        WHERE jurusan = %s
    """, (jurusan,))
    
    data = cur.fetchall()
    cur.close()

    # kalau jurusan tidak ditemukan
    if len(data) == 0:
        return "Tidak ada data jurusan tersebut"

    df = pd.DataFrame(data, columns=[
        'jurusan', 'nama_pkl', 'jarak', 'fasilitas', 'reputasi'
    ])

    # ubah kategori ke angka
    mapping_jarak = {'Dekat': 3, 'Sedang': 2, 'Jauh': 1}
    mapping_fasilitas = {'Lengkap': 3, 'Cukup': 2, 'Kurang': 1}
    mapping_reputasi = {'Sangat Baik': 3, 'Baik': 2, 'Cukup': 1}

    df['jarak'] = df['jarak'].map(mapping_jarak)
    df['fasilitas'] = df['fasilitas'].map(mapping_fasilitas)
    df['reputasi'] = df['reputasi'].map(mapping_reputasi)

    X = df[['jarak', 'fasilitas', 'reputasi']]
    y = df['nama_pkl']

    model = DecisionTreeClassifier()
    model.fit(X, y)

    input_user = [[
        mapping_jarak[jarak],
        mapping_fasilitas[fasilitas],
        mapping_reputasi[reputasi]
    ]]

    hasil = model.predict(input_user)

    return hasil[0]