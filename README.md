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

## 📝 Add Attributes for a Complete BOM

To include project metadata (like COMPANY, PROJECT, and VERSION) in the exported Excel BOM, make sure to define these attributes in your Eagle schematic:

### ✅ Required Attributes

- `COMPANY` – Your company or organization name
- `PROJECT` – Project name (also used as default Excel file name)
- `VERSION` – Hardware or schematic version

### 📌 How to Add in Eagle

1. Open your schematic in Eagle
2. Go to **Edit → Attributes...**
3. Click **New** to add each attribute:
   - `Name`: `COMPANY`, `PROJECT`, or `VERSION`
   - `Value`: Fill with appropriate content
4. Click **OK** to save

Once added, QuickBOM will automatically extract these values into the BOM header when you export.

![GlobalAttributes](https://github.com/user-attachments/assets/7fc87db8-6615-4f2e-992c-91b28f024626)

---

## 📦 Files in Release

- `QuickBOM.exe` – portable executable, no installation needed

---

## 📢 Feedback

Found a bug or have a feature request?  
Open an issue or start a discussion!

![QuickBOM](https://github.com/user-attachments/assets/c047afc6-c62c-455b-8ddb-dcd1337f6ffb)

![BuildedBOM](https://github.com/user-attachments/assets/d8a669ba-2ad5-4f52-814d-c83b561ced25)

