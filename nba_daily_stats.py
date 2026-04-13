import pandas as pd
from nba_api.stats.endpoints import playergamelogs
import time

def get_multi_season_gamelogs(seasons_list):
    # This list will hold the DataFrame for each season temporarily
    all_seasons_data = []
    
    for season in seasons_list:
        print(f"Fetching gamelogs for the {season} season...")
        
        try:
            # Query the API for the current season in the loop
            gamelogs_endpoint = playergamelogs.PlayerGameLogs(season_nullable=season, season_type_nullable='Regular Season')
            df = gamelogs_endpoint.get_data_frames()[0]
            
            # Explicitly add a column to tag which season this data came from
            df['SEASON_QUERIED'] = season 
            
            # Append this season's DataFrame to our master list
            all_seasons_data.append(df)
            print(f"Successfully fetched {len(df)} rows for {season}.")
            
        except Exception as e:
            print(f"X An error occurred while fetching {season}: {e}")
            
        # RATE LIMITER: Pause for 2 seconds before the next loop iteration
        # Do not remove this or the NBA will block your IP!
        time.sleep(2)
        
    # After the loop finishes, merge all DataFrames in the list into one
    if all_seasons_data:
        print("\nMerging datasets...")
        # ignore_index=True resets the row numbers so they go from 0 to N smoothly
        combined_df = pd.concat(all_seasons_data, ignore_index=True)
        return combined_df
    else:
        print("No data was fetched.")
        return None

# --- Execution ---

# 1. Define the seasons you want to scrape
seasons_to_scrape = ['2024-25', '2025-26']

# 2. Run the function
combined_gamelogs_df = get_multi_season_gamelogs(seasons_to_scrape)

# 3. View the results
if combined_gamelogs_df is not None:
    pd.set_option('display.max_columns', None)
    
    print(f"\nFinal Combined Dataset Size: {len(combined_gamelogs_df)} total player-games")
    
    # Let's pull a random sample of 10 rows to verify both seasons are in there
    columns_to_show = ['SEASON_QUERIED', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GAME_DATE', 'MATCHUP', 'PTS']
    print("\nRandom sample of the combined data:")
    print(combined_gamelogs_df[columns_to_show].sample(10))
    

    # combined_gamelogs_df.to_csv('nba_master_gamelogs.csv', index=False)