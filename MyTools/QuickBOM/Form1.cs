using ClosedXML.Excel;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Xml.Linq;

namespace EagleBOM {
    public partial class Form1 : Form {
        private List<GroupedPart> _lastParsedBOM = new();

        public Form1() {
            InitializeComponent();
            groupBox1.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left;// | AnchorStyles.Right;
            dataGridView1.Dock = DockStyle.Fill;

        }

        private void button1_Click(object sender, EventArgs e) {
            using OpenFileDialog dialog = new OpenFileDialog();
            dialog.Filter = "Eagle Schematic Files (*.sch)|*.sch";
            dialog.Title = "Select Eagle Schematic";

            if (dialog.ShowDialog() == DialogResult.OK) {
                string filePath = dialog.FileName;
                textBox1.Text = filePath;

                _lastParsedBOM = ParseEagleSch(filePath)
    .OrderBy(p => p.Designators.Split(',').FirstOrDefault()?.Trim(), StringComparer.OrdinalIgnoreCase)
    .ToList();
                dataGridView1.DataSource = _lastParsedBOM;

                // Rename and reorder columns
                dataGridView1.Columns[nameof(GroupedPart.Quantity)].HeaderText = "QTD";
                dataGridView1.Columns[nameof(GroupedPart.Designators)].HeaderText = "DESIGNATORS";
                dataGridView1.Columns[nameof(GroupedPart.PN)].HeaderText = "PN";

                dataGridView1.Columns[nameof(GroupedPart.Quantity)].DisplayIndex = 0;
                dataGridView1.Columns[nameof(GroupedPart.PN)].DisplayIndex = 1;
                dataGridView1.Columns[nameof(GroupedPart.Designators)].DisplayIndex = 2;

                dataGridView1.Columns[nameof(GroupedPart.Description)].HeaderText = "DESCRIPTION";
                dataGridView1.Columns[nameof(GroupedPart.Package)].HeaderText = "PACKAGE";
                dataGridView1.Columns[nameof(GroupedPart.Value)].HeaderText = "VALUE";

                dataGridView1.ScrollBars = ScrollBars.Vertical;


                // Auto-size all columns
                dataGridView1.AutoResizeColumns(DataGridViewAutoSizeColumnsMode.AllCells);

                // Compute total column width
                int totalWidth = dataGridView1.RowHeadersVisible ? dataGridView1.RowHeadersWidth : 0;
                foreach (DataGridViewColumn col in dataGridView1.Columns)
                    totalWidth += col.Width;

                totalWidth += SystemInformation.VerticalScrollBarWidth + 0;

                // Resize groupBox and form
                if (totalWidth > 800) {
                    groupBox1.Width = totalWidth + groupBox1.Padding.Left + groupBox1.Padding.Right + 0;
                    this.Width = groupBox1.Left + groupBox1.Width + 30;
                }
            }
        }

        private void button2_Click(object sender, EventArgs e) {

            if (_lastParsedBOM == null || !_lastParsedBOM.Any()) {
                MessageBox.Show("No BOM data to export. Please load a schematic first.");
                return;
            }

            string defaultFileName = "BOM"; // fallback

            try {
                var doc = XDocument.Load(textBox1.Text);
                var projectAttr = doc.Descendants("attribute")
                    .FirstOrDefault(a => (string?)a.Attribute("name") == "PROJECT");

                if (projectAttr != null)
                    defaultFileName = projectAttr.Attribute("value")?.Value ?? "BOM";
            }
            catch {
                // fallback stays as "BOM" if parsing fails
            }

            using var saveDialog = new SaveFileDialog {
                Filter = "Excel files (*.xlsx)|*.xlsx",
                Title = "Save BOM Excel",
                FileName = defaultFileName + ".xlsx"
            };

            if (saveDialog.ShowDialog() == DialogResult.OK) {
                string path = saveDialog.FileName;

                try {
                    var doc = XDocument.Load(textBox1.Text);
                    var attrs = doc.Descendants("attribute")
                        .Where(a => a.Attribute("name") != null && a.Attribute("value") != null).GroupBy(a => a.Attribute("name")?.Value)
                        .Where(g => !string.IsNullOrWhiteSpace(g.Key))
                        .ToDictionary(g => g.Key, g => g.First().Attribute("value")?.Value ?? "");

                    using var workbook = new ClosedXML.Excel.XLWorkbook();
                    var ws = workbook.Worksheets.Add("BOM");

                    int row = 1;

                    if (checkBox1.Checked) {
                        // Header block
                       

                        if (attrs.TryGetValue("COMPANY", out var company)) {
                            ws.Cell(row, 1).Value = "COMPANY";
                            ws.Cell(row, 1).Style.Font.Bold = true;
                            ws.Cell(row++, 2).Value = company;
                        }

                        if (attrs.TryGetValue("PROJECT", out var project)) {
                            ws.Cell(row, 1).Value = "PROJECT";
                            ws.Cell(row, 1).Style.Font.Bold = true;
                            ws.Cell(row++, 2).Value = project;
                        }

                        if (attrs.TryGetValue("VERSION", out var version)) {
                            ws.Cell(row, 1).Value = "VERSION";
                            ws.Cell(row, 1).Style.Font.Bold = true;
                            ws.Cell(row++, 2).Value = version;
                        }

                        // BOM Summary
                        int uniqueParts = _lastParsedBOM.Count;
                        int totalQuantity = _lastParsedBOM.Sum(p => p.Quantity);

                        ws.Cell(row, 1).Value = "UNIQUE PART NUMBERS";
                        ws.Cell(row, 1).Style.Font.Bold = true;
                        ws.Cell(row++, 2).Value = uniqueParts;

                        ws.Cell(row, 1).Value = "TOTAL QUANTITY OF PARTS";
                        ws.Cell(row, 1).Style.Font.Bold = true;
                        ws.Cell(row++, 2).Value = totalQuantity;

                        // Align all values to left
                        ws.Column(2).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Left;

                        row++; // empty line before table
                    }

                    // Table headers
                    ws.Cell(row, 1).Value = "QTD";
                    ws.Cell(row, 2).Value = "PN";
                    ws.Cell(row, 3).Value = "DESIGNATORS";
                    //ws.Cell(row, 4).Value = "DESCRIPTION";
                    //ws.Cell(row, 5).Value = "PACKAGE";
                    //ws.Cell(row, 6).Value = "VALUE";
                    var headerRow = ws.Row(row);
                    headerRow.Style.Font.Bold = true;
                    headerRow.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;

                    // Data rows
                    foreach (var part in _lastParsedBOM) {
                        row++;

                        var sortedDesignators = string.Join(", ",
                            part.Designators
                                .Split(new[] { ',', ' ' }, StringSplitOptions.RemoveEmptyEntries)
                                .OrderBy(d => d, StringComparer.OrdinalIgnoreCase)
                        );

                        ws.Cell(row, 1).Value = part.Quantity;
                        ws.Cell(row, 2).Value = part.PN;
                        ws.Cell(row, 3).Value = sortedDesignators;

                        var dataRow = ws.Row(row);
                        dataRow.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                    }


                    ws.Columns().AdjustToContents();

                    // Apply yellow background to QTD, PN, DESIGNATORS
                    // Apply yellow background to header row only (QTD, PN, DESIGNATORS)
                    ws.Range(headerRow.RowNumber(), 1, headerRow.RowNumber(), 3)
                      .Style.Fill.BackgroundColor = XLColor.Yellow;

                    workbook.SaveAs(path);

                    MessageBox.Show("Excel exported successfully.");
                }
                catch (Exception ex) {
                    MessageBox.Show("Error exporting: " + ex.Message);
                }
            }
        }


        private string Escape(string value) {
            if (string.IsNullOrEmpty(value))
                return "";
            return $"\"{value.Replace("\"", "\"\"")}\"";
        }

        private List<GroupedPart> ParseEagleSch(string path) {
            XDocument doc = XDocument.Load(path);

            var ignoredPrefixes = textBox2.Text.Split(',')
                .Select(p => p.Trim().ToUpper())
                .Where(p => !string.IsNullOrWhiteSpace(p))
                .ToList();

            var pnKeys = textBox3.Text.Split(',')
                .Select(k => k.Trim())
                .Where(k => !string.IsNullOrWhiteSpace(k))
                .ToList();

            var parts = new List<(string Designator, string Value, string Package, string PN, string Description)>();
            var deviceAttrs = new Dictionary<(string, string, string), Dictionary<string, string>>();

            foreach (var lib in doc.Descendants("library")) {
                string libName = lib.Attribute("name")?.Value ?? "";
                foreach (var deviceset in lib.Descendants("deviceset")) {
                    string dsName = deviceset.Attribute("name")?.Value ?? "";
                    foreach (var device in deviceset.Descendants("device")) {
                        string devName = device.Attribute("name")?.Value ?? "";
                        var tech = device.Element("technologies")?.Element("technology");

                        var attrs = new Dictionary<string, string>();
                        if (tech != null) {
                            foreach (var attr in tech.Elements("attribute")) {
                                string key = attr.Attribute("name")?.Value ?? "";
                                string val = attr.Attribute("value")?.Value ?? "";
                                if (!string.IsNullOrEmpty(key))
                                    attrs[key] = val;
                            }
                        }

                        deviceAttrs[(libName, dsName, devName)] = attrs;
                    }
                }
            }

            foreach (var p in doc.Descendants("part")) {
                string name = p.Attribute("name")?.Value ?? "";
                if (ignoredPrefixes.Any(prefix => name.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)))
                    continue;

                string value = p.Attribute("value")?.Value ?? "";
                string lib = p.Attribute("library")?.Value ?? "";
                string devset = p.Attribute("deviceset")?.Value ?? "";
                string device = p.Attribute("device")?.Value ?? "";

                string pn = "";
                string desc = "";
                string pkg = device;

                foreach (string key in pnKeys) {
                    var attr = p.Elements("attribute").FirstOrDefault(a => (string)a.Attribute("name") == key);
                    if (attr != null) {
                        pn = attr.Attribute("value")?.Value ?? "";
                        break;
                    }
                }

                var descAttr = p.Elements("attribute").FirstOrDefault(a => (string)a.Attribute("name") == "VALUE");
                if (descAttr != null)
                    desc = descAttr.Attribute("value")?.Value ?? "";

                if (string.IsNullOrEmpty(pn) || string.IsNullOrEmpty(desc)) {
                    deviceAttrs.TryGetValue((lib, devset, device), out var attrs);

                    if (string.IsNullOrEmpty(pn) && attrs != null) {
                        foreach (string key in pnKeys) {
                            if (attrs.TryGetValue(key, out var altPn)) {
                                pn = altPn;
                                break;
                            }
                        }
                    }

                    if (string.IsNullOrEmpty(desc) && attrs != null && attrs.TryGetValue("VALUE", out var altDesc))
                        desc = altDesc;
                }

                parts.Add((Designator: name, Value: value, Package: pkg, PN: pn, Description: desc));
            }

            var grouped = parts
                .Where(p => !string.IsNullOrEmpty(p.PN))
                .GroupBy(p => p.PN)
                .Select(g => new GroupedPart {
                    PN = g.Key,
                    Description = g.Select(x => x.Description).FirstOrDefault(x => !string.IsNullOrWhiteSpace(x)) ?? "",
                    Package = g.Select(x => x.Package).FirstOrDefault(x => !string.IsNullOrWhiteSpace(x)) ?? "",
                    Value = g.Select(x => x.Value).FirstOrDefault(x => !string.IsNullOrWhiteSpace(x)) ?? "",
                    Quantity = g.Count(),
                    Designators = string.Join(", ", g.Select(p => p.Designator).OrderBy(d => Regex.Match(d, @"\D+").Value).ThenBy(d => int.TryParse(Regex.Match(d, @"\d+").Value, out var n) ? n : 0))
                })
                .ToList();

            return grouped;
        }

        private void Form1_Load(object sender, EventArgs e) {

        }
    }

    public class GroupedPart {
        public string PN { get; set; }
        public string Description { get; set; }
        public string Package { get; set; }
        public string Value { get; set; }
        public int Quantity { get; set; }
        public string Designators { get; set; }
    }
}
