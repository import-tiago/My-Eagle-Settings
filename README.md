
# My Autodesk EAGLE Settings and Tools

A collection of utilities, scripts, ULPs, and other tools for personal use with Autodesk EAGLE.

# QuickBOM

**QuickBOM** is a lightweight Windows tool for generating clean, ready-to-use Excel BOMs directly from Autodesk EAGLE `.sch` schematic files.

Designed to help electronics developers streamline BOM generation with just a few clicks.

---

## Features

- Load Eagle `.sch` schematic files
- Parse and group parts by **Part Number**
- Export to `.xlsx` with:
  - Clean headers: `QTD`, `PN`, `DESIGNATORS`
  - Highlighted header row
  - Auto-adjusted columns
  - Project metadata: `COMPANY`, `PROJECT`, `VERSION`, `URL`
  - BOM summary with total quantity and unique part count
- Customizable settings:
  - Define prefixes to ignore (e.g., `TP`, `DNP`, `MNT`)
  - Support multiple attribute keys for Part Number
- Uses `PROJECT` name as default export filename

---

## How to Use

1. Click **Open** and select an Eagle `.sch` file  
2. (Optional) Configure ignored prefixes and part number fields  
3. Click **Export** to generate your Excel BOM  

---

## Adding Project Attributes

For a complete BOM export, define these attributes in your Eagle schematic:

| Attribute  | Description                        |
|------------|------------------------------------|
| `COMPANY`  | Company or organization name       |
| `PROJECT`  | Project name (used as filename)    |
| `VERSION`  | Hardware or schematic version      |
| `URL`      | (Optional) repository or webpage   |

### How to Add in Eagle

1. Open your schematic  
2. Go to **Edit → Attributes...**  
3. Click **New** and enter the attribute name and value  
4. Click **OK** to save  

> QuickBOM will automatically extract and include these in the export.

![GlobalAttributes](https://github.com/user-attachments/assets/7fc87db8-6615-4f2e-992c-91b28f024626)

---

## Screenshots

### QuickBOM Application  
![QuickBOM](https://github.com/user-attachments/assets/c047afc6-c62c-455b-8ddb-dcd1337f6ffb)

### Exported BOM  
![BuildedBOM](https://github.com/user-attachments/assets/d8a669ba-2ad5-4f52-814d-c83b561ced25)

---

## Download

Get the latest version from the [Releases](https://github.com/import-tiago/My-Eagle-Settings/releases) section.

> Download `QuickBOM vX.Y.zip` and run — no installation required.

---

## Contributing & Feedback

Suggestions, improvements, and bug reports are welcome.  
Feel free to open an issue or submit a pull request.
