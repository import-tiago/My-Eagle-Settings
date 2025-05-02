# My Autodesk EAGLE Settings and Tools

Autodesk EAGLE - Set of utilities, scripts, ULPs and other useful things for my own use and personal needs.


# 🚀 QuickBOM v1.0

**QuickBOM** is a lightweight Windows tool for generating clean, ready-to-use Excel BOMs directly from Autodesk Eagle `.sch` schematic files.

---

## ✨ Features

- ✅ **Import Eagle schematic (.sch)** and parse parts automatically  
- ✅ **Group components by Part Number**
- ✅ **Export BOM to `.xlsx`** with:
  - Bold headers: `QTD`, `PN`, `DESIGNATORS`
  - Yellow-highlighted header row
  - Project metadata (COMPANY, PROJECT, VERSION, URL)
  - BOM summary (unique parts, total part quantity)
- ✅ **Ignore part prefixes** (e.g. `TP`, `DNP`, `MNT`) via custom filter
- ✅ **Customizable Part Number field keys**
- ✅ Smart Excel layout with:
  - Auto-sized columns
  - Centered headers
  - Left-aligned values
- ✅ Export uses the PROJECT name as default file name

---

## 📂 How to Use

1. Click **"Open"** to load an Eagle `.sch` file.  
2. Adjust **ignored prefixes** and **part number key fields** if needed.  
3. Click **"Export"** to generate a styled Excel `.xlsx`.

---

## 📦 Files in Release

- `QuickBOM.exe` – portable executable, no installation needed

---

## 📢 Feedback

Found a bug or have a feature request?  
Open an issue or start a discussion!

![QuickBOM](https://github.com/user-attachments/assets/c047afc6-c62c-455b-8ddb-dcd1337f6ffb)

![BuildedBOM](https://github.com/user-attachments/assets/d8a669ba-2ad5-4f52-814d-c83b561ced25)

