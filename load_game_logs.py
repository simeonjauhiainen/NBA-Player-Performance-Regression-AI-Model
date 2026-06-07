from db_connection import get_connection
import pandas as pd
import sys
from nba_api.stats.endpoints import playergamelogs
import time

def get_multi_season_gamelogs(seasons_list):
    all_seasons_data = []
    
    # Retrieve all the NBA data from the API
    for season in seasons_list:
        print(f"Fetching {season}...")
        try:
            gamelogs_endpoint = playergamelogs.PlayerGameLogs(season_nullable=season)
            df = gamelogs_endpoint.get_data_frames()[0]
            all_seasons_data.append(df)
            print(f"Successfully fetched {len(df)} rows for {season}")
        except Exception as e:
            print(f"Error fetching {season}: {e}")
            sys.exit()
        time.sleep(2)
        
    # Merge all DataFrames in the list into one
    if all_seasons_data:
        return pd.concat(all_seasons_data, ignore_index=True)
    return None

# Helper to convert time string formats into decimal minutes
def convert_min_to_decimal(time_str):
    if pd.isna(time_str):
        return 0.0
    try:
        if isinstance(time_str, (int, float)):
            return float(time_str)
        parts = str(time_str).split(':')
        if len(parts) == 2:
            return float(parts[0]) + (float(parts[1]) / 60.0)
        return float(time_str)
    except:
        return 0.0

def insert_raw_gamelogs(df):
    if df is None or df.empty:
        print("No data was fetched. Database update skipped.")
        return
    
    # Define the exact columns matching schema
    raw_cols = [
        'SEASON_YEAR', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION',
        'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA',
        'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB',
        'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'PLUS_MINUS', 'AVAILABLE_FLAG'
    ]
    export_df = df[raw_cols]
    
    # Clean data types for MySQL
    export_df['GAME_DATE'] = pd.to_datetime(export_df['GAME_DATE']).dt.date
    export_df['MIN'] = export_df['MIN'].apply(convert_min_to_decimal).round(2)
    
    float_cols = ['FG_PCT', 'FG3_PCT', 'FT_PCT']
    for col in float_cols:
        export_df[col] = pd.to_numeric(export_df[col], errors='coerce').fillna(0.0).astype(float)
        
    int_cols = ['PLAYER_ID', 'TEAM_ID', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 
                'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'PLUS_MINUS', 'AVAILABLE_FLAG']
    for col in int_cols:
        export_df[col] = pd.to_numeric(export_df[col], errors='coerce').fillna(0).astype(int)
        
    # Fill any null strings to prevent database constraint errors
    export_df['WL'] = export_df['WL'].fillna('')
    export_df['MATCHUP'] = export_df['MATCHUP'].fillna('')

    data_to_insert = [tuple(row) for row in export_df.to_numpy()]

    # Insert into database
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("Truncating old raw_player_game_logs table...")
        cursor.execute("TRUNCATE TABLE raw_player_game_logs")
        
        insert_query = """
            INSERT INTO raw_player_game_logs (
                season_year, player_id, player_name, team_id, team_abbreviation, 
                team_name, game_id, game_date, matchup, wl, min, fgm, fga, 
                fg_pct, fg3m, fg3a, fg3_pct, ftm, fta, ft_pct, oreb, dreb, 
                reb, ast, tov, stl, blk, blka, pf, pfd, pts, plus_minus, available_flag
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        print("Executing bulk insertion...")
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        print(f"Success! {cursor.rowcount} full raw box scores inserted into the database.")

    except Exception as e:
        print(f"Database error during export: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    seasons_to_scrape = ['2024-25', '2025-26']
    game_logs = get_multi_season_gamelogs(seasons_to_scrape)
    insert_raw_gamelogs(game_logs)