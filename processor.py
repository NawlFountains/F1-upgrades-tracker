import os
import pdfplumber
import pandas as pd

TABLE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "lines"}

def get_clean_team_name(text_line: str) -> str | None:
    """ Detects and standarize teams names using anchor keywords.
    
    Args:
        text_line (str): text line that possible contains a team name.
        
    Returns:
        str | None: Unifided comercial named, or None if doesn't match.
    """
    TEAM_KEYWORDS = {
        "red bull": "Red Bull Racing",
        "ferrari": "Scuderia Ferrari",
        "mercedes": "Mercedes F1 Team",
        "mclaren": "McLaren",
        "aston martin": "Aston Martin",
        "alpine": "Alpine F1 Team",
        "williams": "Williams Racing",
        "haas": "Haas F1 Team",
        "audi": "Audi F1 Team",
        "sauber": "Sauber / Audi",
        "rb": "Racing Bulls / RB",
        "visa cash": "Racing Bulls / RB",
        "cadillac": "Cadillac"
    }
    
    line_lower = text_line.lower()
    for keyword, standard_name in TEAM_KEYWORDS.items():
        if keyword in line_lower:
            return standard_name
    return None

def parse_fia_table(table):
    """
    Turn one pdfplumber table (list of rows) into a list of dicts:
    component / reason / differences / description.
 
    Each real row starts with a row number ("1", "2", ...). Any row after
    that with exactly one filled cell is a wrapped continuation of the
    previous row's reason/differences/description — we know which field
    it belongs to because column position stays consistent within a table.
    """
    entries = []
    current = None
    col_role = {}  # column index -> field name, for the entry being built
 
    for row in table:
        filled = [(i, c.strip()) for i, c in enumerate(row) if c and c.strip()]
        if not filled:
            continue
 
        first_idx, first_val = filled[0]
 
        if first_idx == 0 and first_val.isdigit():
            closed_entry = current
            if closed_entry:
                entries.append(closed_entry)
 
            rest = filled[1:]
            if not rest:
                current = None
                continue
 
            _, component = rest[0]
            other_cells = rest[1:]
 
            new_entry = {
                "component": component.replace("\n", " "),
                "reason": None,
                "differences": None,
                "description": None,
            }
 
            if col_role:
                for idx, val in other_cells:
                    field = col_role.get(idx)
                    if field:
                        new_entry[field] = val.replace("\n", " ")
            else:
                for (idx, val), field in zip(other_cells, ("reason", "differences", "description")):
                    new_entry[field] = val.replace("\n", " ")
                    col_role[idx] = field
 
            if closed_entry:
                for field in ("reason", "differences"):
                    if not new_entry[field]:
                        new_entry[field] = closed_entry[field]
 
            if closed_entry and new_entry["description"] and new_entry["description"][0].islower():
                closed_entry["description"] = (closed_entry["description"] + " " + new_entry["description"]).strip()
                new_entry["description"] = closed_entry["description"]
            elif not new_entry["description"] and closed_entry:
                new_entry["description"] = closed_entry["description"]
 
            current = new_entry
            continue
 
        if current and len(filled) == 1:
            idx, val = filled[0]
            field = col_role.get(idx)
            if field:
                current[field] = (current[field] + " " + val).strip()
 
    if current:
        entries.append(current)
 
    return entries
 
 
def parse_fia_car_presentation(pdf_path: str) -> pd.DataFrame:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)
 
    rows = []
    current_team = None
 
    with pdfplumber.open(pdf_path) as pdf:
        for _, page in enumerate(pdf.pages[1:], start=1):
 
            text = page.extract_text() or ""
            for line in text.split("\n"):
                team = get_clean_team_name(line)  # your existing function
                if team:
                    current_team = team
 
                if current_team and "no updates submitted" in line.lower():
                    rows.append({
                        "team": current_team,
                        "component": "None",
                        "reason": "No updates submitted for this event",
                        "differences": "None",
                        "description": "None",
                    })
 
            for table in page.extract_tables(table_settings=TABLE_SETTINGS):
                for entry in parse_fia_table(table):
                    rows.append({
                        "team": current_team or "Unknown Team",
                        **entry,
                    })
 
    return pd.DataFrame(rows)
 
 
if __name__ == "__main__":
    archivo_local = "2026_hungarian_grand_prix_car_presentation_submissions.pdf"
    df = parse_fia_car_presentation(archivo_local)
    df.to_csv("fia_updates.csv", index=False)
    print(f"Wrote {len(df)} rows to fia_updates.csv")
