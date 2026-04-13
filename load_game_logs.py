from db_connection import get_connection
from nba_daily_stats import get_multi_season_gamelogs
import pandas as pd

def clean_value(value):
    if pd.isna(value):
        return None
    return value

def load_data():
    seasons = ['2025-26']
    df = get_multi_season_gamelogs(seasons)

    if df is None:
        print("No data fetched.")
        return

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"]).dt.date

    conn = get_connection()
    if conn is None:
        print("Database connection failed.")
        return

    cursor = conn.cursor()

    insert_query = """
    INSERT INTO player_game_logs (
        player_id, player_name, team_id, team_abbreviation, game_id,
        game_date, matchup, wl, min, pts, reb, ast, stl, blk, tov,
        fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, pf, plus_minus, season_queried
    ) VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        pts = VALUES(pts),
        reb = VALUES(reb),
        ast = VALUES(ast),
        stl = VALUES(stl),
        blk = VALUES(blk),
        tov = VALUES(tov),
        plus_minus = VALUES(plus_minus)
    """

    for index, row in df.iterrows():
        values = (
            clean_value(row["PLAYER_ID"]),
            clean_value(row["PLAYER_NAME"]),
            clean_value(row["TEAM_ID"]),
            clean_value(row["TEAM_ABBREVIATION"]),
            clean_value(row["GAME_ID"]),
            clean_value(row["GAME_DATE"]),
            clean_value(row["MATCHUP"]),
            clean_value(row["WL"]),
            clean_value(row["MIN"]),
            clean_value(row["PTS"]),
            clean_value(row["REB"]),
            clean_value(row["AST"]),
            clean_value(row["STL"]),
            clean_value(row["BLK"]),
            clean_value(row["TOV"]),
            clean_value(row["FGM"]),
            clean_value(row["FGA"]),
            clean_value(row["FG3M"]),
            clean_value(row["FG3A"]),
            clean_value(row["FTM"]),
            clean_value(row["FTA"]),
            clean_value(row["OREB"]),
            clean_value(row["DREB"]),
            clean_value(row["PF"]),
            clean_value(row["PLUS_MINUS"]),
            clean_value(row["SEASON_QUERIED"])
        )

        cursor.execute(insert_query, values)

    conn.commit()
    print("Data inserted successfully!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_data()