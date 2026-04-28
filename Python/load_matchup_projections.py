import pandas as pd
import mysql.connector

# -------------------------------
# DB CONNECTION
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediction_modeldb"
)

cursor = conn.cursor()

# -------------------------------
# LOAD CSV (CHANGE FILE NAME)
# -------------------------------
df = pd.read_csv("all_matchups_projections.csv")

# -------------------------------
# CLEAN COLUMN NAMES
# -------------------------------
df.columns = df.columns.str.strip().str.lower()

df = df.rename(columns={
    "player_n": "player_name",
    "team_ab": "team_abbreviation",
    "opponen": "opponent",
    "proj_pts": "pred_points",
    "proj_reb": "pred_rebounds",
    "proj_ast": "pred_assists"
})

# -------------------------------
# CLEAN DATA
# -------------------------------
df["player_name"] = df["player_name"].str.strip()
df["team_abbreviation"] = df["team_abbreviation"].str.strip()
df["opponent"] = df["opponent"].str.strip()

df["pred_points"] = pd.to_numeric(df["pred_points"], errors="coerce")
df["pred_rebounds"] = pd.to_numeric(df["pred_rebounds"], errors="coerce")
df["pred_assists"] = pd.to_numeric(df["pred_assists"], errors="coerce")

df = df.dropna(subset=[
    "player_name",
    "team_abbreviation",
    "opponent",
    "pred_points",
    "pred_rebounds",
    "pred_assists"
])

# -------------------------------
# CALCULATE PRA
# -------------------------------
df["pred_pra"] = (
    df["pred_points"] +
    df["pred_rebounds"] +
    df["pred_assists"]
)

print("Rows ready to insert:", len(df))


# -------------------------------
# INSERT QUERY
# -------------------------------
insert_query = """
INSERT INTO matchup_projections (
    player_name,
    team_abbreviation,
    opponent,
    pred_points,
    pred_rebounds,
    pred_assists,
    pred_pra
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    pred_points = VALUES(pred_points),
    pred_rebounds = VALUES(pred_rebounds),
    pred_assists = VALUES(pred_assists),
    pred_pra = VALUES(pred_pra);
"""

# -------------------------------
# INSERT LOOP
# -------------------------------
for _, row in df.iterrows():
    cursor.execute(insert_query, (
        row["player_name"],
        row["team_abbreviation"],
        row["opponent"],
        round(row["pred_points"], 2),
        round(row["pred_rebounds"], 2),
        round(row["pred_assists"], 2),
        round(row["pred_pra"], 2)
    ))

conn.commit()

print( Teammate projections inserted successfully)

cursor.close()
conn.close()