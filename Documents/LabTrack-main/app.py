import smtplib
from email.message import EmailMessage
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()  # 🔄 Betölti a .env tartalmát

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # 💡 Betöltjük biztonságosan


# ✨ Adatbázis kapcsolat
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


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
            return redirect(next_page) if next_page else redirect(url_for('labor'))  # ⬅️ itt történik az irányítás
        else:
            msg = 'Hibás felhasználónév vagy jelszó!'

    return render_template('login.html', msg=msg, show_tabla=True)




# 🚪 Kijelentkezés
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



# ---------------------------------------------
# Hibák emailben történő értesítése
def send_error_email(uzenet):
    msg = EmailMessage()
    msg.set_content(uzenet)
    msg["Subject"] = "⚠️ LabTrack Hibaértesítés"
    msg["From"] = "flask@vallalat.hu"       # Módosítsd a saját címre
    msg["To"] = "it-support@vallalat.hu"     # Módosítsd a saját címre

    try:
        with smtplib.SMTP("smtp.vallalat.hu", 587) as server:  # Módosítsd az SMTP szerver elérhetőségére
            server.starttls()
            server.login("flask@vallalat.hu", "jelszo")         # A hitelesítő adatok
            server.send_message(msg)
    except Exception as e:
        print("E-mail küldési hiba:", e)

# Hibák logolása és értesítésének küldése
def log_es_ertesit(forras, hibauzenet):
    full_message = f"[{forras}] Hiba: {hibauzenet}"
    print(full_message)
    send_error_email(full_message)

# MySQL kapcsolat létrehozása
def get_connection():
    return mysql.connector.connect(
    host="localhost",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="LabTrack"
)
# -----------------------------------------------------------------------------------
# Route: Adatbevitel űrlap (/beviteli)

# Globális változó a friss adatok ellenőrzésére (pl. a POST beszúrásoknál)
last_known_time = None

@app.route("/beviteli", methods=["GET", "POST"])
def beviteli():
    if request.method == "POST":
        # Űrlap értékek kiolvasása
        anyag_nev    = request.form.get("anyag_nev")
        idh_val      = request.form.get("idh")
        eredeti_sarzs = request.form.get("sarzs_szam_A")  # elmentjük az eredeti beírt értéket
        sarzs_szam_B = request.form.get("sarzs_szam_B")
        sorszam      = request.form.get("sorszam")
        erkezesi_ido = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        allapot      = "Folyamatban..."

        # Ellenőrzés: sarzs kezdődjön nagy A-val
        if not (eredeti_sarzs and eredeti_sarzs[0] == "A"):
            flash("Hiba: A sarzsszámnak nagy 'A'-val kell kezdődnie!", "error")
            return redirect(url_for("beviteli"))

        if not (sorszam and "/" in sorszam):
            flash("Hiba: A minta sorszámnak tartalmaznia kell egy '/' jelet!", "error")
            return redirect(url_for("beviteli"))

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # 🔁 Automatikus sarzsszám generálás, ha már létezik
            def generate_unique_sarzs(sarzs_alap):
                check_cursor = conn.cursor()
                check_cursor.execute("""
                    SELECT sarzs_szam_A FROM labtrack_data WHERE sarzs_szam_A LIKE %s
                    UNION
                    SELECT sarzs_szam_A FROM labtrack_archive WHERE sarzs_szam_A LIKE %s
                """, (sarzs_alap + '%', sarzs_alap + '%'))
                existing = [row[0] for row in check_cursor.fetchall()]
                check_cursor.close()

                if sarzs_alap not in existing:
                    return sarzs_alap

                i = 1
                while f"{sarzs_alap}_{i}" in existing:
                    i += 1
                return f"{sarzs_alap}_{i}"

            sarzs_szam_A = generate_unique_sarzs(eredeti_sarzs)

            if sarzs_szam_A != eredeti_sarzs:
                flash(f"A megadott sarzsszám már létezett. Automatikusan módosítottuk: **{sarzs_szam_A}**", "info")

            # 🔢 Beszúrás az új mezőnevekkel (vacuum_eredmeny_A/B/idő stb.)
            sql = """
                INSERT INTO labtrack_data 
                (paszta_nev, idh, sarzs_szam_A, sarzs_szam_B, erkezesi_ido, kezdes_ido, befejezes, labor_ido, monogram,
                allapot, indok, vacuum_eredmeny_A, vacuum_eredmeny_B, vacuum_ido_A, vacuum_ido_B, sorszam, kiszereles_datum, kiszereles_oka)
                VALUES (%s, %s, %s, %s, %s, NULL, NULL, NULL, NULL,
                        %s, NULL, NULL, NULL, NULL, NULL, %s, NULL, NULL)
            """
            values = (
                anyag_nev, idh_val, sarzs_szam_A, sarzs_szam_B, erkezesi_ido,
                allapot, sorszam
            )

            cursor.execute(sql, values)
            conn.commit()
            flash(f"Adatok sikeresen rögzítve: **{sarzs_szam_A}**", "success")

        except mysql.connector.Error as err:
            print("Hiba az adat beszúrásakor:", err)
            flash(f"Hiba az adat beszúrásakor: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("beviteli.html")


# -----------------------------------------------------------------------------------
# Route: Laboros adatbevitel (/labor)
@app.route("/labor", methods=["GET", "POST"])
@login_required
def labor():
    # Ha az űrlapot elküldték (POST kérés)
    if request.method == "POST":
        sarzs_szam_A = request.form.get("sarzs_szam_A")
        monogram = current_user.username  # Bejelentkezett felhasználó neve
        
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Lekérdezzük az aktuális sarzshoz tartozó állapotot
            cursor.execute(
                "SELECT allapot, kezdes_ido, befejezes FROM labtrack_data WHERE sarzs_szam_A = %s LIMIT 1",
                (sarzs_szam_A,)
            )
            row = cursor.fetchone()

            if row and row["allapot"] == "NOK":
                flash("Ez a paszta 'NOK' állapotban van, nem módosítható.")
            elif row:
                # Időbélyeg rögzítése és monogram frissítése
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "UPDATE labtrack_data SET kezdes_ido = %s, monogram = %s WHERE sarzs_szam_A = %s",
                    (current_time, monogram, sarzs_szam_A)
                )

                # Ha befejezés már van, újraszámoljuk a labor időt
                cursor.execute(
                    "SELECT kezdes_ido, befejezes FROM labtrack_data WHERE sarzs_szam_A = %s LIMIT 1",
                    (sarzs_szam_A,)
                )
                updated_row = cursor.fetchone()
                if updated_row and updated_row["kezdes_ido"] and updated_row["befejezes"]:
                    start_dt = updated_row["kezdes_ido"]
                    finish_dt = updated_row["befejezes"]

                    # Átalakítás datetime objektummá, ha szükséges
                    if isinstance(start_dt, str):
                        start_dt = datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
                    if isinstance(finish_dt, str):
                        finish_dt = datetime.strptime(finish_dt, "%Y-%m-%d %H:%M:%S")

                    labor_time = (finish_dt - start_dt).total_seconds() / 60  # percben
                    cursor.execute(
                        "UPDATE labtrack_data SET labor_ido = %s WHERE sarzs_szam_A = %s",
                        (labor_time, sarzs_szam_A)
                    )
            conn.commit()
        except mysql.connector.Error as err:
            log_es_ertesit("labor adatbevitel", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
        return redirect(url_for("tabla"))
    
    # GET esetén: sarzsszámokat lekérjük a legördülőhöz
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sarzs_szam_A FROM labtrack_data ORDER BY sarzs_szam_A DESC")
        sarzsszamok = [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as err:
        flash(f"Hiba a sarzsszámok lekérdezésekor: {err}")
        sarzsszamok = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("labor.html", sarzsszamok=sarzsszamok)
# -----------------------------------------------------------------------------------
# Route: vacuum adatbevitel (/vacuum)

@app.route("/vacuum", methods=["GET", "POST"])
@login_required
def vacuum():
    if request.method == "POST":
        sarzs_szam = request.form.get("sarzs_szam_A")
        oldal = request.form.get("oldal")
        ido_most = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM labtrack_data WHERE sarzs_szam_A = %s", (sarzs_szam,))
            row = cursor.fetchone()

            if row and row["allapot"] == "NOK":
                flash("Ez a paszta NOK, nem módosítható.")
            else:
                update_fields = {}

                if oldal == "both":
                    for oldal_val in ["A", "B"]:
                        eredmeny_mezo = f"vacuum_eredmeny_{oldal_val}"
                        ido_mezo = f"vacuum_ido_{oldal_val}"
                        uj_eredmeny = request.form.get(eredmeny_mezo)
                        eddigi = row.get(eredmeny_mezo) or ""
                        ido_rögzítve = row.get(ido_mezo)

                        uj_sorozat = f"{eddigi},{uj_eredmeny}" if eddigi else uj_eredmeny
                        update_fields[eredmeny_mezo] = uj_sorozat

                        if "ok" in uj_sorozat and not ido_rögzítve:
                            update_fields[ido_mezo] = ido_most
                else:
                    eredmeny_mezo = f"vacuum_eredmeny_{oldal}"
                    ido_mezo = f"vacuum_ido_{oldal}"
                    uj_eredmeny = request.form.get(eredmeny_mezo)
                    eddigi = row.get(eredmeny_mezo) or ""
                    ido_rögzítve = row.get(ido_mezo)

                    uj_sorozat = f"{eddigi},{uj_eredmeny}" if eddigi else uj_eredmeny
                    update_fields[eredmeny_mezo] = uj_sorozat

                    if "ok" in uj_sorozat and not ido_rögzítve:
                        update_fields[ido_mezo] = ido_most

                # SQL lekérdezés összeállítása
                set_clause = ", ".join([f"{mezo} = %s" for mezo in update_fields.keys()])
                sql = f"UPDATE labtrack_data SET {set_clause} WHERE sarzs_szam_A = %s"
                cursor.execute(sql, list(update_fields.values()) + [sarzs_szam])
                conn.commit()

        except mysql.connector.Error as err:
            log_es_ertesit("vacuum művelet", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for("vacuum"))

    # GET kérés: sarzs számok lekérdezése
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sarzs_szam_A FROM labtrack_data ORDER BY sarzs_szam_A DESC")
        sarzsszamok = [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as err:
        flash(f"Hiba a sarzsszámok lekérdezésekor: {err}")
        sarzsszamok = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("vacuum.html", sarzsszamok=sarzsszamok)


# -----------------------------------------------------------------------------------
@app.route("/eredmeny", methods=["GET", "POST"])
@login_required
def eredmeny():
    if request.method == "POST":
        sarzs_szam_A = request.form.get("sarzs_szam_A")
        allapot = request.form.get("allapot", "").upper()
        indok = request.form.get("indok", "")
        monogram = current_user.username  # Bejelentkezett felhasználó neve

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Ellenőrizzük, hogy módosítható-e ez a sarzsszám
            cursor.execute("SELECT * FROM labtrack_data WHERE sarzs_szam_A = %s LIMIT 1", (sarzs_szam_A,))
            row = cursor.fetchone()

            if row and row["allapot"] == "NOK":
                flash("Ez a paszta NOK állapotú, nem módosítható.")
            elif row:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Frissítjük a befejezést, állapotot, indokot és monogramot
                cursor.execute("""
                    UPDATE labtrack_data 
                    SET befejezes = %s, allapot = %s, indok = %s, monogram = %s 
                    WHERE sarzs_szam_A = %s
                """, (now, allapot, indok, monogram, sarzs_szam_A))

                # Labor idő újraszámolása, ha mindkét időpont megvan
                cursor.execute("SELECT kezdes_ido, befejezes FROM labtrack_data WHERE sarzs_szam_A = %s", (sarzs_szam_A,))
                t = cursor.fetchone()

                if t and t["kezdes_ido"] and t["befejezes"]:
                    start = t["kezdes_ido"]
                    end = t["befejezes"]

                    # Ha dátum sztring, alakítsuk át datetime objektummá
                    if isinstance(start, str):
                        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                    if isinstance(end, str):
                        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

                    labor_minutes = (end - start).total_seconds() / 60
                    cursor.execute("UPDATE labtrack_data SET labor_ido = %s WHERE sarzs_szam_A = %s", (labor_minutes, sarzs_szam_A))

            conn.commit()
        except mysql.connector.Error as err:
            log_es_ertesit("eredmény művelet", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for("tabla"))

    # GET kérés esetén: betöltjük a sarzsszámokat legördülőhöz
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sarzs_szam_A FROM labtrack_data ORDER BY sarzs_szam_A DESC")
        sarzsszamok = [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as err:
        flash(f"Hiba a sarzsszámok lekérdezésekor: {err}")
        sarzsszamok = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("eredmeny.html", sarzsszamok=sarzsszamok)



# -----------------------------------------------------------------------------------
# Route: Kiszerelés rögzítése (/kiszereles)
@app.route("/kiszereles", methods=["GET", "POST"])
@login_required
def kiszereles():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Az összes aktív rekord megjelenítése a labtrack_data táblából
        cursor.execute("SELECT paszta_nev, sarzs_szam_A, sarzs_szam_B, allapot FROM labtrack_data")
        data = cursor.fetchall()
    except mysql.connector.Error as err:
        log_es_ertesit("kiszereles művelet", str(err))
        data = []
    
    if request.method == "POST":
        sarzs_szam_A = request.form.get("sarzs_szam_A")
        try:
            # Új kurzor a teljes rekord lekérdezéséhez
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM labtrack_data WHERE sarzs_szam_A = %s LIMIT 1", (sarzs_szam_A,))
            row = cursor.fetchone()
            if row:
                # A kiszerelés dátumát a NOW() segítségével állítjuk be, és a kiszerelés okát 'Kiszerelve'-re
                # Ezeket nem a row értékei közül vesszük, hanem felülírjuk
                insert_sql = """
                    INSERT INTO labtrack_archive (
                        paszta_nev, idh, sarzs_szam_A, sarzs_szam_B, erkezesi_ido,
                        kezdes_ido, befejezes, labor_ido, monogram, allapot, indok,
                        vacuum_eredmeny_A, vacuum_eredmeny_B, vacuum_ido_A, vacuum_ido_B,
                        sorszam, kiszereles_datum, kiszereles_oka
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, NOW(), 'Kiszerelve'
                    )
                """
                values = (
                    row.get("paszta_nev"), row.get("idh"), row.get("sarzs_szam_A"), row.get("sarzs_szam_B"),
                    row.get("erkezesi_ido"), row.get("kezdes_ido"), row.get("befejezes"), row.get("labor_ido"),
                    row.get("monogram"), row.get("allapot"), row.get("indok"),
                    row.get("vacuum_eredmeny_A"), row.get("vacuum_eredmeny_B"),
                    row.get("vacuum_ido_A"), row.get("vacuum_ido_B"),
                    row.get("sorszam")
)

                cursor.execute(insert_sql, values)
                # Töröljük a rekordot a labtrack_data táblából
                delete_sql = "DELETE FROM labtrack_data WHERE sarzs_szam_A = %s"
                cursor.execute(delete_sql, (sarzs_szam_A,))
                conn.commit()
                print("Archíválás sikeres a sarzs_szam_A:", sarzs_szam_A)
            else:
                print("Nincs rekord a megadott sarzs_szam_A alapján:", sarzs_szam_A)
        except mysql.connector.Error as err:
            log_es_ertesit("kiszereles művelet", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return redirect(url_for("kiszereles"))
    else:
        conn.commit()
        cursor.close()
        conn.close()
    
    return render_template("kiszereles.html", data=data)


# -----------------------------------------------------------------------------------
# Route: Archív adatok megtekintése (/archiv)
@app.route("/archiv")
def archiv():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM labtrack_archive")
        data = cursor.fetchall()
    except mysql.connector.Error as err:
        log_es_ertesit("kiszereles művelet", str(err))
        data = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template("archiv.html", data=data)

# -----------------------------------------------------------------------------------
# Route: Összes adat megtekintése (/tabla)
@app.route("/tabla")
def tabla():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM labtrack_data")
        data = cursor.fetchall()
    except mysql.connector.Error as err:
        log_es_ertesit("kiszereles művelet", str(err))
        data = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template("tabla.html", data=data)

# -----------------------------------------------------------------------------------
# Route: Ellenőrzés a legfrissebb erkezési idő alapján (/ellenoriz)
@app.route("/ellenoriz")
def ellenoriz():
    global last_known_time
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MAX(erkezesi_ido) AS last_time FROM labtrack_data")
        result = cursor.fetchone()
    except mysql.connector.Error as err:
        log_es_ertesit("kiszereles művelet", str(err))
        result = {"last_time": None}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    aktualis_ido = result["last_time"]
    if last_known_time is None:
        last_known_time = aktualis_ido
        return jsonify({"uj_adat": False})
    if aktualis_ido and aktualis_ido > last_known_time:
        last_known_time = aktualis_ido
        return jsonify({"uj_adat": True})
    return jsonify({"uj_adat": False})


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

# -----------------------------------------------------------------------------------
# Hiba kezelése: minden kivétel esetén email küldése és hibaoldal megjelenítése

@app.errorhandler(Exception)
def handle_exception(e):
    # Itt értesítjük emailben is az IT csapatot, majd egy hibaoldalt jelenítünk meg
    send_error_email(str(e))
    return render_template("hiba.html", hiba=str(e)), 500

# -----------------------------------------------------------------------------------
# Alapértelmezett útvonal: átirányítás a /tabla-ra
@app.route("/")
def index():
    return redirect(url_for("tabla"))

if __name__ == "__main__":
    app.run(debug=True)
