import pandas as pd

# ── Load both raw CSV files ────────────────────────────────────────────────────
female = pd.read_csv("API_SL.UEM.1524.FE.NE.ZS_DS2_en_csv_v2_10367.csv", skiprows=4)
male   = pd.read_csv("API_SL.UEM.1524.MA.NE.ZS_DS2_en_csv_v2_10368.csv", skiprows=4)

year_cols = [str(y) for y in range(1960, 2026)]

# ── Clean function ─────────────────────────────────────────────────────────────
def clean(df, gender):
    df = df[["Country Name", "Country Code"] + year_cols].copy()
    df = df.dropna(subset=year_cols, how="all")
    df = df[df["Country Code"].str.len() == 3]
    df = df.melt(id_vars=["Country Name", "Country Code"],
                 var_name="Year",
                 value_name="Unemployment Rate (%)")
    df["Year"] = df["Year"].astype(int)
    df["Gender"] = gender
    df = df.dropna(subset=["Unemployment Rate (%)"])
    df["Unemployment Rate (%)"] = df["Unemployment Rate (%)"].round(2)
    return df

# ── Clean both datasets ────────────────────────────────────────────────────────
female_clean = clean(female, "Female")
male_clean   = clean(male,   "Male")

# ── Combine into one file ──────────────────────────────────────────────────────
combined = pd.concat([female_clean, male_clean], ignore_index=True)
combined = combined.sort_values(["Country Name", "Year", "Gender"]).reset_index(drop=True)

# ── Save cleaned file ──────────────────────────────────────────────────────────
combined.to_csv("youth_unemployment_cleaned.csv", index=False)

print("✅ Done! Cleaned file saved as youth_unemployment_cleaned.csv")
print(f"   Total rows    : {len(combined)}")
print(f"   Countries     : {combined['Country Name'].nunique()}")
print(f"   Years         : {combined['Year'].min()} to {combined['Year'].max()}")