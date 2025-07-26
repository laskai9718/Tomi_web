#!/bin/bash
# A script a progi mappából indítja el az app-napi.py-t

# Lépjünk be abba a mappába, ahol a script található
cd "$(dirname "$0")"

# Aktiváljuk a virtuális környezetet, ha van
source venv/bin/activate 2>/dev/null

# Indítsuk el az alkalmazást
python3 app-napi.py
