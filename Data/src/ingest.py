import pandas as pd
import sqlite3
import os

RAW_PATH = "Data/salaries.csv"
DB_PATH = "Data/jobs.db"

def load_and_clean():
    df = pd.read_csv(RAW_PATH)
    
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    
    df = df.drop_duplicates()
    
    df["experience_level"] = df["experience_level"].map({
        "EN": "Entry-level", "MI": "Mid-level", 
        "SE": "Senior", "EX": "Executive"
    })
    
    df["company_size"] = df["company_size"].map({
        "S": "Small", "M": "Medium", "L": "Large"
    })
    
    df["employment_type"] = df["employment_type"].map({
        "FT": "Full-time", "PT": "Part-time", 
        "CT": "Contract", "FL": "Freelance"
    })
    
    df["processed_at"] = pd.Timestamp.now().isoformat()
    
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    return df

def save_to_sqlite(df):
    os.makedirs("Data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("jobs", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved {len(df)} records to {DB_PATH}")

if __name__ == "__main__":
    df = load_and_clean()
    save_to_sqlite(df)