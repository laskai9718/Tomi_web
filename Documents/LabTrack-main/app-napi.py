import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import io
from flask import send_file
import xlsxwriter
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()  # 🔄 Betölti a .env tartalmát

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # 💡 Betöltjük biztonságosan
#alap beállítások-------------------------------------------------------------

# ✨ Adatbázis kapcsolat
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

print("User:", os.getenv("DB_USER"))
print("Password:", os.getenv("DB_PASSWORD"))

# 👤 Flask-Login beállítások
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email



@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return User(row['id'], row['username'], row['email'])
    return None


# 📝 Regisztráció
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    next_page = request.args.get('next')  # ⬅️ lekérjük a továbbküldési célt

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hash_pw = hashlib.sha256(password.encode()).hexdigest()

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Ez a felhasználónév már létezik!'
        else:
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hash_pw))
            db.commit()
            msg = 'Sikeres regisztráció! Jelentkezz be!'
            return redirect(url_for('login', next=next_page))  # ⬅️ továbbküldés loginre és tovább

    return render_template('register.html', msg=msg)

# 🔐 Bejelentkezés
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    next_page = request.args.get('next')  # ⬅️ ezt olvassuk ki a queryből

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hash_pw = hashlib.sha256(password.encode()).hexdigest()

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hash_pw))
        account = cursor.fetchone()

        if account:
            user_obj = User(account['id'], account['username'], account['email'])
            login_user(user_obj)
            msg = 'Sikeres bejelentkezés!'
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))  # ⬅️ itt történik az irányítás
        else:
            msg = 'Hibás felhasználónév vagy jelszó!'

    return render_template('login.html', msg=msg, show_tabla=False)



# 🚪 Kijelentkezés
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))





@app.route("/dashboard/export")
@login_required
def export_dashboard_xlsx():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM labtrack_archive ORDER BY befejezes DESC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Export hiba: {e}")
        return redirect(url_for("dashboard"))

    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet("Minták")

    # Fejlécek
    headers = list(data[0].keys()) if data else []
    for col, key in enumerate(headers):
        ws.write(0, col, key)

    # Sorok
    for rownum, row in enumerate(data, 1):
        for col, key in enumerate(headers):
            ws.write(rownum, col, str(row.get(key, "")))

    wb.close()
    output.seek(0)
    return send_file(output,
                     download_name="dashboard_export.xlsx",
                     as_attachment=True)


def get_connection():
    return mysql.connector.connect(
    host="localhost",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="LabTrack"
)



def get_tests_info(pasta_name):
    name_lower = pasta_name.lower() if pasta_name else ""
    tests = []
    if "1500" in name_lower:
        tests.extend([("7 napos teszt", 7), ("oldódási teszt", 7)])
    elif "2900" in name_lower:
        tests.append(("4 napos teszt", 4))
    elif "2800" in name_lower:
        tests.append(("14 napos teszt", 14))
    elif "henrico" in name_lower:
        tests.append(("24 H teszt", 1))
    return tests


def human_readable_timedelta(tdelta):
    total = int(tdelta.total_seconds())
    if total < 0:
        return "Lejárt"
    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    return f"{days} nap, {hours} óra, {minutes} perc"


def col_name(prefix, test_label):
    return f"{prefix}_{test_label.lower().replace(' ', '_')}"


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM labtrack_archive ORDER BY befejezes DESC")
        data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Hiba az adatok lekérdezésekor: {err}")
        data = []
    finally:
        try:
            cursor.close()
        except: pass
    try:
        conn.close()
    except: pass


    nok_darab = sum(
        1 for row in data
        if row.get("allapot", "").strip().upper() == "NOK"
    )

    tasks = []
    now = datetime.now()
    for row in data:
        if row.get("allapot", "").strip().upper() == "NOK":
            continue
        befejezes = row.get("befejezes")
        if not befejezes:
            continue

        pasta = row.get("paszta_nev")
        for label, days in get_tests_info(pasta):
            status_col = col_name("teszt_kesz", label)
            if row.get(status_col):
                continue
            sched = befejezes + timedelta(days=days)
            tasks.append({
                "id": row["id"],
                "pasta": pasta,
                "befejezes": befejezes.strftime("%Y-%m-%d %H:%M"),
                "test_label": label,
                "scheduled_date": sched.strftime("%Y-%m-%d %H:%M"),
                "remaining": human_readable_timedelta(sched - now)
            })

    return render_template(
        "dashboard.html",
        tasks=tasks,
        nok_darab=nok_darab
    )


@app.route('/adatlapom')
@login_required
def profil_adatok():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('adatlapom.html', user=user_data)



#eltéti adatok frissítése----------------------------------------------------------------

def structure_setup_and_save():
    from datetime import datetime, timedelta

    # 1) Lekérjük az el nem osztott mintákat
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, paszta_nev, befejezes
        FROM labtrack_archive
        WHERE raklap_azonosito IS NULL
          AND allapot != 'NOK'
        ORDER BY paszta_nev, befejezes
    """)
    unassigned = cursor.fetchall()

    # 2) Lekérjük a már kiosztott statisztikákat
    cursor.execute("""
        SELECT paszta_nev, raklap_azonosito, COUNT(*) AS cnt
        FROM labtrack_archive
        WHERE raklap_azonosito IS NOT NULL
          AND doboz_index IS NOT NULL
        GROUP BY paszta_nev, raklap_azonosito
    """)
    assigned_stats = cursor.fetchall()
    cursor.close()
    conn.close()

    # 3) Inicializáljuk a rackeket és terhelésüket
    pallets = {f"R-{i}": None for i in range(1, 10)}  # R-1…R-9
    load    = {f"R-{i}": 0    for i in range(1, 10)}
    material_to_pallet = {}                           # paszta_nev → rack

    # 4) Visszavezetjük a már kiosztott anyagokat
    for row in assigned_stats:
        mat = (row["paszta_nev"] or "").strip()
        pal = row["raklap_azonosito"]
        cnt = row["cnt"]
        if mat not in material_to_pallet:
            material_to_pallet[mat] = pal
            if pal in pallets:
                pallets[pal] = mat
        load[pal] += cnt

    # 5) Új anyagokra kiosztunk racket, ha kell
    #    – legelső üres, kevésbé terhelt R-1…R-9
    #    – ha nincs, R-0 marad fallback
    unique_mats = []
    for s in unassigned:
        mat = (s["paszta_nev"] or "ismeretlen").strip()
        if mat not in unique_mats:
            unique_mats.append(mat)

    for mat in unique_mats:
        if mat in material_to_pallet:
            continue
        for pid, assigned in pallets.items():
            if assigned is None and load[pid] < 280:
                material_to_pallet[mat] = pid
                pallets[pid] = mat
                break
        else:
            material_to_pallet[mat] = "R-0"

    # 6) Doboztípusú csoportosítás: rack → lista dobozobjektum
    #    minden dobozobjektum: { material: str, samples: [ {...}, ... ] }
    box_groups = {}
    for sample in unassigned:
        mat = (sample["paszta_nev"] or "ismeretlen").strip()
        pal = material_to_pallet.get(mat, "R-0")

        if pal not in box_groups:
            box_groups[pal] = []

        groups = box_groups[pal]
        if groups and groups[-1]["material"] == mat and len(groups[-1]["samples"]) < 5:
            groups[-1]["samples"].append(sample)
        else:
            groups.append({ "material": mat, "samples": [sample] })

    # 7) SQL-update: minden rack, minden dobozcsoport → doboz_index
    update_sql = """
        UPDATE labtrack_archive
           SET raklap_azonosito = %s,
               doboz_index      = %s
         WHERE id = %s
    """
    conn = get_connection()
    cursor = conn.cursor()
    for pal, groups in box_groups.items():
        for box_idx, group in enumerate(groups, start=1):
            for samp in group["samples"]:
                cursor.execute(update_sql,
                               (pal, box_idx, samp["id"]))
    conn.commit()
    cursor.close()
    conn.close()



def get_eltet_structure():
    from datetime import datetime, timedelta

    # 1) Adatok lekérése a reklamációs mezőkkel együtt
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            id,
            raklap_azonosito,
            doboz_index,
            paszta_nev,
            befejezes,
            sarzs_szam_A,
            sarzs_szam_B,
            verified,
            reklamacio_datum,
            reklamacio_megjegyzes
        FROM labtrack_archive
        WHERE allapot != 'NOK'
          AND raklap_azonosito IS NOT NULL
          AND doboz_index      IS NOT NULL
        ORDER BY raklap_azonosito, doboz_index
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # 2) Raklap–doboz struktúra építése
    structure = {}
    now = datetime.utcnow()

    for r in rows:
        raklap      = r["raklap_azonosito"]
        doboz_index = r["doboz_index"] - 1          # 0-index
        r["lejar"]  = r["befejezes"] + timedelta(days=365)
        # reklamációs mezők
        r["reklamacio_datum"]      = r.get("reklamacio_datum")
        r["reklamacio_megjegyzes"] = r.get("reklamacio_megjegyzes")

        # ha még nincs entry a raklaphoz, inicializáljuk 56 dobozzal
        if raklap not in structure:
            structure[raklap] = [None] * 56

        # ha ez a doboz még üres, hozzunk létre alestruktúrát
        if structure[raklap][doboz_index] is None:
            structure[raklap][doboz_index] = {
                "items": [],
                "status": "",
                "ready": False
            }

        # hozzáadjuk a mintát a doboz „items” listájához
        structure[raklap][doboz_index]["items"].append(r)

    # 3) Státusz és „ready” mező kitöltése
    for raklap, dobozok in structure.items():
        for i in range(len(dobozok)):  # 0…55
            box   = dobozok[i] or {"items": []}
            mintak = box["items"]

            if not mintak:
                box["status"] = "empty"
            else:
                lej_datumok = [m["lejar"] for m in mintak]
                if any(d < now for d in lej_datumok):
                    box["status"] = "expired"
                elif any(d < now + timedelta(days=30) for d in lej_datumok):
                    box["status"] = "soon"
                else:
                    box["status"] = "ok"

            box["ready"]   = (len(mintak) == 5)
            dobozok[i]    = box

    return structure


@app.route("/verify_sample", methods=["POST"])
@login_required
def verify_sample():
    data = request.get_json()
    sarzs = data.get("sarzs")
    raklap = data.get("mat")
    doboz_index = int(data.get("box"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Megkeressük a mintát a sarzsszám alapján
    cursor.execute("""
        SELECT id, paszta_nev, befejezes, verified
        FROM labtrack_archive
        WHERE sarzs_szam_A = %s OR sarzs_szam_B = %s
    """, (sarzs, sarzs))
    minta = cursor.fetchone()

    if not minta:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "❌ Nincs ilyen sarzsszám!"})

    # Ellenőrizzük, hogy nem töltötték-e már be
    if minta["verified"]:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "❌ Ezt a mintát már egyszer bepakolták!"})

    # Frissítés: jelöljük verified-re és hozzárendeljük a dobozhoz
    cursor.execute("""
        UPDATE labtrack_archive
        SET verified = TRUE,
            raklap_azonosito = %s,
            doboz_index = %s
        WHERE id = %s
    """, (raklap, doboz_index, minta["id"]))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status": "ok",
        "message": f"✅ Sikeresen bepakolva: {sarzs} → {raklap} Doboz #{doboz_index}"
    })

@app.route("/")
@login_required
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM labtrack_archive ORDER BY befejezes DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    nok_darab = sum(1 for row in data if row.get("allapot", "").strip().upper() == "NOK")
    tasks = []

    now = datetime.now()
    for row in data:
        if row.get("allapot", "").strip().upper() == "NOK":
            continue
        befejezes = row.get("befejezes")
        if not befejezes:
            continue
        pasta = row.get("paszta_nev")
        for label, days in get_tests_info(pasta):
            status_col = col_name("teszt_kesz", label)
            if row.get(status_col):
                continue
            sched = befejezes + timedelta(days=days)
            tasks.append({
                "id": row["id"],
                "pasta": pasta,
                "befejezes": befejezes.strftime("%Y-%m-%d %H:%M"),
                "test_label": label,
                "scheduled_date": sched.strftime("%Y-%m-%d %H:%M"),
                "remaining": human_readable_timedelta(sched - now)
            })

    return render_template("dashboard.html", tasks=tasks, nok_darab=nok_darab)
@app.route("/eltet")
@login_required
def eltet():
    structure_setup_and_save()
    structure = get_eltet_structure()
    return render_template("eltet.html", structure=structure)


@app.route("/update_sample", methods=["POST"])
@login_required
def update_sample():
    sample_id = int(request.form["id"])
    sarzs_A = request.form["sarzs_szam_A"]
    sarzs_B = request.form["sarzs_szam_B"]
    befejezes = request.form["befejezes"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE labtrack_archive
        SET sarzs_szam_A = %s,
            sarzs_szam_B = %s,
            befejezes = %s
        WHERE id = %s
    """, (sarzs_A, sarzs_B, befejezes, sample_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Minta frissítve!")
    return redirect(url_for("eltet"))

# 🔍 Sarzsszám kereső funkció
@app.route("/keres_sarzs", methods=["POST"])
@login_required
def keres_sarzs():
    data = request.get_json()
    sarzs = data.get("sarzs")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT raklap_azonosito, doboz_index, paszta_nev, befejezes
        FROM labtrack_archive
        WHERE sarzs_szam_A = %s OR sarzs_szam_B = %s
    """, (sarzs, sarzs))
    eredmeny = cursor.fetchone()
    cursor.close()
    conn.close()

    if not eredmeny:
        return jsonify({"status": "error", "message": "❌ Nem található ilyen sarzsszám!"})

    lejar = eredmeny["befejezes"] + timedelta(days=365)

    return jsonify({
        "status": "ok",
        "raklap": eredmeny["raklap_azonosito"],
        "doboz": eredmeny["doboz_index"],
        "anyag": eredmeny["paszta_nev"],
        "lejar": lejar.strftime("%Y-%m-%d")
    })

# 📤 Eltéti minták Excel export
@app.route("/eltet/export")
@login_required
def export_eltet_xlsx():
    structure = get_eltet_structure()

    output   = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet    = workbook.add_worksheet("Eltéti minták")

    # 1) Fejlécek: reklamációs oszlopokkal kiegészítve
    headers = [
        "Raklap", "Doboz #", "Sorszám",
        "Anyag", "Sarzsszám", "Lejárat",
        "Befejezés", "Verified",
        "Reklamáció dátum", "Reklamáció megjegyzés"
    ]
    for col, title in enumerate(headers):
        sheet.write(0, col, title)

    # 2) Sorok írása
    row = 1
    for raklap, boxes in structure.items():
        for box_num, box in enumerate(boxes, start=1):
            if not box or not box["items"]:
                continue

            for idx, item in enumerate(box["items"], start=1):
                sarzs       = item.get("sarzs_szam_A") or item.get("sarzs_szam_B") or ""
                lejar       = item.get("lejar")
                bef         = item.get("befejezes")
                anyag       = item.get("paszta_nev", "")
                verified    = "✔️" if item.get("verified") else ""
                rekl_datum  = item.get("reklamacio_datum")
                rekl_megj   = item.get("reklamacio_megjegyzes") or ""

                sheet.write(row, 0, raklap)
                sheet.write(row, 1, box_num)
                sheet.write(row, 2, idx)
                sheet.write(row, 3, anyag)
                sheet.write(row, 4, sarzs)
                sheet.write(
                    row, 5,
                    lejar.strftime("%Y-%m-%d") if lejar else ""
                )
                sheet.write(
                    row, 6,
                    bef.strftime("%Y-%m-%d") if bef else ""
                )
                sheet.write(row, 7, verified)
                sheet.write(
                    row, 8,
                    rekl_datum.strftime("%Y-%m-%d %H:%M")
                    if rekl_datum else ""
                )
                sheet.write(row, 9, rekl_megj)

                row += 1

    workbook.close()
    output.seek(0)
    return send_file(
        output,
        download_name="elteti_export.xlsx",
        as_attachment=True
    )

@app.route("/complete", methods=["POST"])
@login_required
def complete():
    sample_id = request.form.get("id")
    test_label = request.form.get("test_label")

    conn = get_connection()
    cursor = conn.cursor()

    col_name_str = col_name("teszt_kesz", test_label)
    cursor.execute(f"""
        UPDATE labtrack_archive
        SET {col_name_str} = TRUE
        WHERE id = %s
    """, (sample_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Mérés lezárva!")
    return redirect(url_for("dashboard"))

@app.route("/remove_for_complaint", methods=["POST"])
@login_required
def remove_for_complaint():
    data      = request.get_json()
    sample_id = data.get("id")
    comment   = data.get("comment", "").strip() or None

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE labtrack_archive
           SET reklamacio_datum      = NOW(),
               reklamacio_megjegyzes = %s
         WHERE id = %s
    """, (comment, sample_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "ok", "id": sample_id})


app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
