import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os

app = Flask(__name__)
EXCEL_FILE = "LabTrack_data.xlsx"

# Megpróbáljuk beolvasni az Excel fájlt, ha nem található, létrehozunk egy üres DataFrame-et a szükséges oszlopokkal
try:
    df = pd.read_excel(EXCEL_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "Paszta név", "IDH", "Sarzs szám A", "Sarzs szám B", "Érkezési idő",
        "Kezdés idő", "Befejezés", "Labor idő", "Monogram", "Állapot", "Indok",
        "Vacuum kezdés", "Vacuum eredmény", "Sorszám", "Kiszerelés oka", "Kiszerelés dátuma"
    ])

# Ha hiányoznak az oszlopok, hozzáadjuk őket
missing_columns = ["Kiszerelés dátuma", "Kiszerelés oka"]
for col in missing_columns:
    if col not in df.columns:
        df[col] = None

df.to_excel(EXCEL_FILE, index=False)
print("Excel fájl frissítve a hiányzó oszlopokkal!")

# -----------------------------------------------------------------------------------
# Route: Beviteli (termelési adatbevitel)
@app.route("/beviteli", methods=["GET", "POST"])
def beviteli():
    if request.method == "POST":
        anyag_nev = request.form.get("anyag_nev")
        idh = request.form.get("idh")
        sarzs_szam_A = request.form.get("sarzs_szam_A")
        sarzs_szam_B = request.form.get("sarzs_szam_B")
        # Automatikusan a jelenlegi dátum–időt rögzítjük
        erkezesi_ido = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sorszam = request.form.get("sorszam")
        allapot = "Folyamatban..."

        try:
            df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                "Paszta név", "IDH", "Sarzs szám A", "Sarzs szám B", "Érkezési idő",
                "Kezdés idő", "Befejezés", "Labor idő", "Monogram", "Állapot", "Indok",
                "Vacuum kezdés", "Vacuum eredmény", "Sorszám", "Kiszerelés oka", "Kiszerelés dátuma"
            ])

        # Ha NOK állapotú paszta már létezik, új sor készül
        if "NOK" in df.loc[df["Sarzs szám A"] == sarzs_szam_A, "Állapot"].values:
            print("Ez a paszta NOK volt, új mérést rögzítek egy új sorban.")
            new_data = pd.DataFrame([[
                anyag_nev, idh, sarzs_szam_A, sarzs_szam_B, erkezesi_ido, None, None, None, None, "Folyamatban...", None, None, None, sorszam, None, None
            ]], columns=df.columns)
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            new_data = pd.DataFrame([[
                anyag_nev, idh, sarzs_szam_A, sarzs_szam_B, erkezesi_ido, None, None, None, None, allapot, None, None, None, sorszam, None, None
            ]], columns=df.columns)
            df = pd.concat([df, new_data], ignore_index=True)

        df.to_excel(EXCEL_FILE, index=False)
        return redirect(url_for("tabla"))
    return render_template("beviteli.html")

# -----------------------------------------------------------------------------------
# Route: Laboros adatbevitel
@app.route("/labor", methods=["GET", "POST"])
def labor():
    if request.method == "POST":
        sarzs_szam_A = request.form["sarzs_szam_A"]
        monogram = request.form["monogram"]

        try:
            df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                "Paszta név", "IDH", "Sarzs szám A", "Sarzs szám B", "Érkezési idő",
                "Kezdés idő", "Befejezés", "Labor idő", "Monogram", "Állapot", "Indok",
                "Vacuum kezdés", "Vacuum eredmény", "Sorszám", "Kiszerelés oka", "Kiszerelés dátuma"
            ])

        if "NOK" in df.loc[df["Sarzs szám A"] == sarzs_szam_A, "Állapot"].values:
            print("Ez a paszta NOK, nem módosítható.")
        else:
            matching_rows = df[df["Sarzs szám A"] == sarzs_szam_A]
            if not matching_rows.empty:
                idx = matching_rows.index[0]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[idx, "Kezdés idő"] = current_time  # automatikus kezdeti idő
                df.at[idx, "Monogram"] = monogram         # a megfelelő sorhoz írjuk
                df["Kezdés idő"] = pd.to_datetime(df["Kezdés idő"], errors='coerce')
                df["Befejezés"] = pd.to_datetime(df["Befejezés"], errors='coerce')
                if pd.notna(df.at[idx, "Kezdés idő"]) and pd.notna(df.at[idx, "Befejezés"]):
                    labor_time = (df.at[idx, "Befejezés"] - df.at[idx, "Kezdés idő"]).total_seconds() / 60
                    df.at[idx, "Labor idő"] = labor_time

        df.to_excel(EXCEL_FILE, index=False)
        print(df.tail())
        return redirect(url_for("tabla"))
    return render_template("labor.html")

# -----------------------------------------------------------------------------------
# Route: Vacuum teszt rögzítése
@app.route("/vacuum", methods=["GET", "POST"])
def vacuum():
    if request.method == "POST":
        sarzs_szam_A = request.form["sarzs_szam_A"]
        vacuum_kezdes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vacuum_eredmeny = request.form["vacuum_eredmeny"]

        try:
            df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                "Paszta név", "IDH", "Sarzs szám A", "Sarzs szám B", "Érkezési idő",
                "Kezdés idő", "Befejezés", "Labor idő", "Monogram", "Állapot", "Indok",
                "Vacuum kezdés", "Vacuum eredmény", "Sorszám", "Kiszerelés oka", "Kiszerelés dátuma"
            ])

        if "NOK" in df.loc[df["Sarzs szám A"] == sarzs_szam_A, "Állapot"].values:
            print("Ez a paszta NOK, nem módosítható.")
        else:
            df.loc[df["Sarzs szám A"] == sarzs_szam_A, ["Vacuum kezdés", "Vacuum eredmény"]] = [vacuum_kezdes, vacuum_eredmeny]

        df.to_excel(EXCEL_FILE, index=False)
        return redirect(url_for("tabla"))
    return render_template("vacuum.html")

# -----------------------------------------------------------------------------------
# Route: TV-n megjelenített táblázat (összes adat)
@app.route("/tabla")
def tabla():
    try:
        df = pd.read_excel(EXCEL_FILE)
        print("Beolvasott adatok:", df.tail())
        data = df.to_dict(orient="records")
    except FileNotFoundError:
        data = []
    return render_template("tabla.html", data=data)

# -----------------------------------------------------------------------------------
# Route: Eredmények rögzítése
@app.route("/eredmeny", methods=["GET", "POST"])
def eredmeny():
    if request.method == "POST":
        sarzs_szam_A = request.form["sarzs_szam_A"]
        allapot = request.form["allapot"]
        indok = request.form.get("indok", "")
        monogram = request.form["monogram"]

        try:
            df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                "Paszta név", "IDH", "Sarzs szám A", "Sarzs szám B", "Érkezési idő",
                "Kezdés idő", "Befejezés", "Labor idő", "Monogram", "Állapot", "Indok",
                "Vacuum kezdés", "Vacuum eredmény", "Sorszám", "Kiszerelés oka", "Kiszerelés dátuma"
            ])

        if "NOK" in df.loc[df["Sarzs szám A"] == sarzs_szam_A, "Állapot"].values:
            print("Ez a paszta NOK, nem módosítható.")
        else:
            matching_rows = df[df["Sarzs szám A"] == sarzs_szam_A]
            if not matching_rows.empty:
                idx = matching_rows.index[0]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[idx, "Befejezés"] = current_time  # automatikus befejezés
                df.at[idx, "Állapot"] = allapot.upper()
                df.at[idx, "Indok"] = indok
                df.at[idx, "Monogram"] = monogram
                df["Kezdés idő"] = pd.to_datetime(df["Kezdés idő"], errors='coerce')
                df["Befejezés"] = pd.to_datetime(df["Befejezés"], errors='coerce')
                if pd.notna(df.at[idx, "Kezdés idő"]) and pd.notna(df.at[idx, "Befejezés"]):
                    labor_time = (df.at[idx, "Befejezés"] - df.at[idx, "Kezdés idő"]).total_seconds() / 60
                    df.at[idx, "Labor idő"] = labor_time

        df.to_excel(EXCEL_FILE, index=False)
        print(df.tail())
        return redirect(url_for("tabla"))
    return render_template("eredmeny.html")

# -----------------------------------------------------------------------------------
# Route: Kiszerelés rögzítése
@app.route("/kiszereles", methods=["GET", "POST"])
def kiszereles():
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Paszta név", "Sarzs szám A", "Sarzs szám B", "Állapot"])
    data = df[["Paszta név", "Sarzs szám A", "Sarzs szám B", "Állapot"]].to_dict(orient="records")

    if request.method == "POST":
        sarzs_szam_A = request.form["sarzs_szam_A"]
        kiszerelt_sor = df[df["Sarzs szám A"] == sarzs_szam_A].copy()
        kiszerelt_sor["Kiszerelés dátuma"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kiszerelt_sor["Kiszerelés oka"] = "Kiszerelve"

        try:
            archive_df = pd.read_excel("LabTrack_archive.xlsx")
        except FileNotFoundError:
            archive_df = pd.DataFrame(columns=["Paszta név", "Sarzs szám A", "Sarzs szám B", "Állapot", "Kiszerelés dátuma", "Kiszerelés oka"])

        archive_df = pd.concat([archive_df, kiszerelt_sor], ignore_index=True)
        archive_df.to_excel("LabTrack_archive.xlsx", index=False)
        df = df[df["Sarzs szám A"] != sarzs_szam_A]
        df.to_excel(EXCEL_FILE, index=False)
        return redirect(url_for("kiszereles"))
    return render_template("kiszereles.html", data=data)

# -----------------------------------------------------------------------------------
# Route: Archív adatok megtekintése
@app.route("/archiv", methods=["GET"])
def archiv():
    try:
        archive_df = pd.read_excel("LabTrack_archive.xlsx")
        data = archive_df.to_dict(orient="records")
    except FileNotFoundError:
        data = []
    return render_template("archiv.html", data=data)

# -----------------------------------------------------------------------------------
# Route: Ellenőrzés a friss adatokra (pl. az Excel fájl módosítási ideje alapján)
last_known_time = os.path.getmtime(EXCEL_FILE)

@app.route("/ellenoriz")
def ellenoriz():
    global last_known_time
    try:
        aktualis_ido = os.path.getmtime(EXCEL_FILE)
    except FileNotFoundError:
        return jsonify({"uj_adat": False})
    if aktualis_ido > last_known_time:
        last_known_time = aktualis_ido
        return jsonify({"uj_adat": True})
    return jsonify({"uj_adat": False})

# -----------------------------------------------------------------------------------
# Alapértelmezett útvonal: átirányítás a táblázathoz
@app.route("/")
def index():
    return redirect(url_for("tabla"))

if __name__ == "__main__":
    app.run(debug=True)
