from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
from datetime import datetime, timedelta
import os



app = Flask(__name__)
app.secret_key = "your-secret-key"  # Állítsd be a titkos kulcsot

EXCEL_FILE = "LabTrack_archive.xlsx"

# Lehetséges teszt típusok (ezeket fogjuk kiírni az Excelbe, ha nem léteznek)
POTENTIAL_TESTS = ["7 napos teszt", "oldódási teszt", "4 napos teszt", "14 napos teszt", "24 H teszt"]


def get_tests_info(pasta_name):
    name_lower = pasta_name.lower()
    tests = []
    if "1500 geneva" in name_lower:
        tests.append(("7 napos teszt", 7))
        tests.append(("oldódási teszt", 7))
    elif "1500 eu" in name_lower:
        tests.append(("oldódási teszt", 7))
    elif "2900" in name_lower:
        tests.append(("4 napos teszt", 4))
    elif "2800" in name_lower:
        tests.append(("14 napos teszt", 14))
    elif "henrico" in name_lower:  # kisbetűs összehasonlítás!
        tests.append(("24 H teszt", 1))
    return tests


def load_excel():
    if not os.path.exists(EXCEL_FILE):
        return None
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Kötelező oszlopok: "Paszta név" és "Befejezés"
        if "Paszta név" not in df.columns or "Befejezés" not in df.columns:
            return None

        # A "Befejezés" oszlop datetime típusú
        df["Befejezés"] = pd.to_datetime(df["Befejezés"], errors='coerce')

        # Létrehozzuk a statusz- és monogram oszlopokat minden lehetséges teszttípusra
        for test in POTENTIAL_TESTS:
            status_col = f"Teszt kész: {test}"
            monogram_col = f"Monogram: {test}"
            if status_col not in df.columns:
                df[status_col] = ""
            if monogram_col not in df.columns:
                df[monogram_col] = ""
        return df
    except Exception as e:
        print("Hiba az Excel beolvasása során:", e)
        return None

def save_excel(df):
    try:
        df.to_excel(EXCEL_FILE, index=False)
        return True
    except Exception as e:
        print("Hiba az Excel mentése során:", e)
        return False

def human_readable_timedelta(tdelta):
    total_seconds = int(tdelta.total_seconds())
    if total_seconds < 0:
        return "Lejárt"
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{days} nap, {hours} óra, {minutes} perc"

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    df = load_excel()
    if df is None:
        flash("Nem sikerült beolvasni az Excel fájlt, vagy a szükséges oszlopok hiányoznak!")
        return render_template("dashboard.html", tasks=[])
    
    pending_tasks = []
    now = datetime.now()

    # Az Excel minden sorára nézünk, majd a paszta neve alapján lekérjük a hozzátartozó teszt feladatokat.
    for idx, row in df.iterrows():
        finished = row["Befejezés"]
        if pd.isna(finished):
            continue  # ha nincs befejezés dátum, kihagyjuk

        pasta = row["Paszta név"]
        tests = get_tests_info(pasta)

        # Minden teszthez külön feladatot adunk hozzá
        for test_label, offset_days in tests:
            status_col = f"Teszt kész: {test_label}"
            # Csak akkor adjuk hozzá, ha az adott teszt még nincs kitöltve
            if row[status_col] == "" or pd.isna(row[status_col]):
                scheduled_date = finished + timedelta(days=offset_days)
                remaining = scheduled_date - now
                pending_tasks.append({
                    "index": idx,
                    "pasta": pasta,
                    "finished": finished.strftime("%Y-%m-%d %H:%M"),
                    "test_label": test_label,
                    "scheduled_date": scheduled_date.strftime("%Y-%m-%d %H:%M"),
                    "remaining": human_readable_timedelta(remaining)
                })
    
    return render_template("dashboard.html", tasks=pending_tasks)

@app.route('/complete', methods=["POST"])
def complete():
    # Az űrlap az Excel sor indexét, a teszt típusát és a monogramot küldi el.
    try:
        idx = int(request.form.get("index"))
    except (ValueError, TypeError):
        flash("Érvénytelen sor azonosító!")
        return redirect(url_for("dashboard"))
    
    test_label = request.form.get("test_label", "").strip()
    monogram = request.form.get("monogram", "").strip()
    
    if not test_label or not monogram:
        flash("Mind a teszt típus, mind a monogram megadása kötelező!")
        return redirect(url_for("dashboard"))
    
    df = load_excel()
    if df is None:
        flash("Nem sikerült beolvasni az Excel fájlt!")
        return redirect(url_for("dashboard"))
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    status_col = f"Teszt kész: {test_label}"
    monogram_col = f"Monogram: {test_label}"
    
    try:
        df.at[idx, status_col] = now_str  # Rögzítjük a kész időt az adott teszthöz
        df.at[idx, monogram_col] = monogram
    except Exception as e:
        flash("Hiba történt a sor frissítésekor!")
        return redirect(url_for("dashboard"))
    
    if not save_excel(df):
        flash("Hiba történt az Excel fájl mentése során!")
        return redirect(url_for("dashboard"))
    
    flash("A mérés sikeresen rögzítve!")
    return redirect(url_for("dashboard"))

@app.route("/ellenoriz")
def ellenoriz():
    try:
        aktualis_ido = os.path.getmtime(EXCEL_FILE)
    except FileNotFoundError:
        return jsonify({"uj_adat": False})

    if "last_known_time" not in globals():
        globals()["last_known_time"] = aktualis_ido

    if aktualis_ido > globals()["last_known_time"]:
        globals()["last_known_time"] = aktualis_ido
        return jsonify({"uj_adat": True})

    return jsonify({"uj_adat": False})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
