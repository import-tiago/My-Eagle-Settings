# My Autodesk EAGLE Settings and Tools

Autodesk EAGLE - Set of utilities, scripts, ULPs and other useful things for my own use and personal needs.

# ⚡ QuickBOM

**QuickBOM** is a lightweight Windows tool for generating clean, ready-to-use Excel BOMs directly from Autodesk Eagle `.sch` schematic files.

Designed to help electronics developers streamline their BOM generation process with just a few clicks.

---

## ✨ Features

- 📂 Load Eagle `.sch` schematic files
- 🔎 Parse and group parts by **Part Number**
- ⬇️ Export to `.xlsx` with:
  - Clean headers: `QTD`, `PN`, `DESIGNATORS`
  - Yellow-highlighted header row
  - Auto-adjusted columns
  - Project metadata: `COMPANY`, `PROJECT`, `VERSION`, `URL`
  - BOM summary: total quantity and unique part numbers
- ⚙️ Custom settings:
  - Define prefixes to ignore (e.g., `TP`, `DNP`, `MNT`)
  - Support multiple attribute keys for Part Number
- 📄 Uses the `PROJECT` name as default file name for exports

---

## 🧪 How to Use

1. Click **Open** and select an Eagle `.sch` file
2. (Optional) Set ignored prefixes and part number field names
3. Click **Export** to generate your Excel BOM

---

## 📝 Add Attributes for a Complete BOM

To include your **project information** in the exported Excel file, make sure to define these attributes in your Eagle schematic:

### Required Attributes

| Attribute  | Description                        |
|------------|------------------------------------|
| `COMPANY`  | Company or organization name       |
| `PROJECT`  | Project name (used as filename)    |
| `VERSION`  | Hardware or schematic version      |
| `URL`      | (Optional) repository or webpage   |

### How to Add in Eagle

1. Open your schematic  
2. Go to **Edit → Attributes...**  
3. Click **New** and enter each attribute name and value  
4. Click **OK** to save

> Once added, QuickBOM will extract and display them in the Excel export.

![GlobalAttributes](https://github.com/user-attachments/assets/7fc87db8-6615-4f2e-992c-91b28f024626)

---

## 🖼 Screenshots

### QuickBOM App
![QuickBOM](https://github.com/user-attachments/assets/c047afc6-c62c-455b-8ddb-dcd1337f6ffb)

### Exported BOM
![BuildedBOM](https://github.com/user-attachments/assets/d8a669ba-2ad5-4f52-814d-c83b561ced25)

---

## 📦 Download

You can find the latest version in the [Releases](https://github.com/import-tiago/My-Eagle-Settings/releases) section.

> Just download `QuickBOM.rar` and run — no installation needed.

---

## 🤝 Contributing & Feedback

Feel free to open issues for bugs, suggestions, or improvements.  
Pull requests are welcome!
