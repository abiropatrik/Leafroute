# Rövid ismertetés
Jelen alkalmazás egy szakdolgozat keretein bellül létrejött környezetbarát Transportation Management System.

A kutatásról, a programról és az eredményekről bővebb információ a szakdolgozat beszámolójában található.

## Futtatás
A fejlesztői környezet felépítését részletesen a beszámoló "BACKEND FELÉPÍTÉSE" fejezete tartalmazza, melynek elolvasása kiemelten fontos a futtatás előtt.

A program megfelelő működéséhez mindenképpen szükséges:
  - Docker Desktop telepítése és beállítása
  - MySQL Workbench telepítése és beállítása
  - Egyéni Django secret key generálása a django_key_generator.py segítségével
  - Google Maps API kulcs beszerzése (e-nélkül nem működik a stage-rétegből dw-rétegbe transzformáló ETL job)

Az API kulcsot és a secret keyt a következő formátumban kell beletenni a .env fájlba:
GOOGLE_MAPS_API_KEY='yourapicode'
DJANGO_SECRET_KEY='yoursecretkey'

Az alkalmazás a make compose-start utasítással indítható el.
