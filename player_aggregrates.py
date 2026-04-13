from db_connection import get_connection
import pandas as pd
import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prediction_modeldb"
        )
    except Error as e:
        print("Connection failed:", e)


conn = get_connection()

if conn is not None:
    print("Connected")

    try:
        query = "SELECT * FROM player_game_logs"
        df = pd.read_sql(query, conn)

        print("Query ran")
        print("Rows:", len(df))
        print(df.head())

    except Exception as e:
        print("Error:", e)

    # changes the field game_date from plain text into a real date type
    # helps python determine what game came before which
    df["game_date"] = pd.to_datetime(df["game_date"])

    # sorts players and dates so each play games are now in order
    df = df.sort_values(by=["player_id", "game_date"])

    player_df = df[df["player_id"] == 2544]

    # computing averages for player aggregrates
    # create new dataframe for last 5 points
    # rolling = last 5, xshift = remove current game, mean = average
    df["last_5_points"] = df.groupby("player_id")["pts"] \
        .transform(lambda x: x.shift(1).rolling(5).mean())

    df["last_5_rebounds"] = df.groupby("player_id")["reb"] \
        .transform(lambda x: x.shift(1).rolling(5).mean())

    df["last_5_assists"] = df.groupby("player_id")["ast"] \
        .transform(lambda x: x.shift(1).rolling(5).mean())

    df["last_5_minutes"] = df.groupby("player_id")["min"].transform(lambda x: x.shift(1).rolling(5).mean())
    df["last_10_minutes"] = df.groupby("player_id")["min"].transform(lambda x: x.shift(1).rolling(10).mean())

    player_df = df[df["player_name"] == "LeBron James"]
    print(player_df[["game_date", "pts", "reb", "ast", "min", "last_5_points"]].tail(10))

    df["fp"] = (
            df["pts"] * 1 +
            df["reb"] * 1.2 +
            df["ast"] * 1.5)

    df["last_5_fp"] = df.groupby("player_id")["fp"].transform(lambda x: x.shift(1).rolling(5).mean())

    df["season_fp"] = df.groupby("player_id")["fp"].transform(lambda x: x.shift(1).expanding().mean())

    df["slate_date"] = df["game_date"]

    df["updated_at"] = pd.Timestamp.now()

aggregates_df = df[[
    "player_id",
    "player_name",
    "game_date",
    "last_5_fp",
    "season_fp",
    "last_5_minutes",
    "last_10_minutes",
    "last_5_points",
    "last_5_rebounds",
    "last_5_assists"
]].copy()

aggregates_df = aggregates_df.rename(columns={"game_date": "slate_date"})
aggregates_df["slate_date"] = pd.to_datetime(aggregates_df["slate_date"], errors="coerce").dt.date
aggregates_df = aggregates_df.dropna(subset=["slate_date"])
aggregates_df["updated_at"] = pd.Timestamp.now()
aggregates_df = aggregates_df.astype(object).where(pd.notnull(aggregates_df), None)

try:
    conn = get_connection()
    cursor = conn.cursor()


    insert_query = """
      INSERT INTO player_aggregates
(player_id, player_name, slate_date, last_5_fp, season_fp, last_5_minutes, last_10_minutes,
 last_5_points, last_5_rebounds, last_5_assists, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    player_name = VALUES(player_name),
    last_5_fp = VALUES(last_5_fp),
    season_fp = VALUES(season_fp),
    last_5_minutes = VALUES(last_5_minutes),
    last_10_minutes = VALUES(last_10_minutes),
    last_5_points = VALUES(last_5_points),
    last_5_rebounds = VALUES(last_5_rebounds),
    last_5_assists = VALUES(last_5_assists),
    updated_at = VALUES(updated_at)
"""

    data_to_insert = [tuple(row) for row in aggregates_df.to_numpy()]

    batch_size = 10

    for i in range(0, len(data_to_insert), batch_size):
        batch = data_to_insert[i:i + batch_size]
        print(f"Trying rows {i} to {i + len(batch) - 1}")
        print(batch)
        cursor.executemany(insert_query, batch)
        conn.commit()
        print(f"Inserted rows: {i + len(batch)}")

    cursor.executemany(insert_query, data_to_insert)
    conn.commit()

    print(cursor.rowcount, "rows inserted into player_aggregates")

except Error as e:
    print("Insert failed:", e)

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
