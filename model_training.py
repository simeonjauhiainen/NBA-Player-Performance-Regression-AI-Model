import sys
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelogs
import time
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.linear_model import LassoCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.impute import SimpleImputer

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

seasons_to_scrape = ['2024-25', '2025-26']
combined_gamelogs_df = get_multi_season_gamelogs(seasons_to_scrape)

if combined_gamelogs_df is not None:
    
    # 1. Base Filters & Date Formatting
    combined_gamelogs_df = combined_gamelogs_df[combined_gamelogs_df['AVAILABLE_FLAG'] == 1]
    combined_gamelogs_df['GAME_DATE'] = pd.to_datetime(combined_gamelogs_df['GAME_DATE'])
    
    # Drop Preseason
    drop_24_25 = (combined_gamelogs_df['SEASON_YEAR'] == '2024-25') & (combined_gamelogs_df['GAME_DATE'] < '2024-10-22')
    drop_25_26 = (combined_gamelogs_df['SEASON_YEAR'] == '2025-26') & (combined_gamelogs_df['GAME_DATE'] < '2025-10-21')
    combined_gamelogs_df = combined_gamelogs_df[~(drop_24_25 | drop_25_26)]
    
    # Drop All-Star Games
    combined_gamelogs_df = combined_gamelogs_df[combined_gamelogs_df['TEAM_ABBREVIATION'].notna()]

    # 2. Simple Indicators
    playoff_24_25 = (combined_gamelogs_df['SEASON_YEAR'] == '2024-25') & (combined_gamelogs_df['GAME_DATE'] >= '2025-04-15')
    playoff_25_26 = (combined_gamelogs_df['SEASON_YEAR'] == '2025-26') & (combined_gamelogs_df['GAME_DATE'] >= '2026-04-14')
    combined_gamelogs_df['IS_PLAYOFF'] = (playoff_24_25 | playoff_25_26).astype(int)
    combined_gamelogs_df['IS_HOME'] = combined_gamelogs_df['MATCHUP'].str.contains('vs.').astype(int)
    combined_gamelogs_df['OPPONENT'] = combined_gamelogs_df['MATCHUP'].str[-3:]

    # Player Days of Rest (FIXED SEASON CONTINUITY)
    combined_gamelogs_df = combined_gamelogs_df.sort_values(by=['PLAYER_ID', 'GAME_DATE'])
    # Added SEASON_YEAR to the groupby
    combined_gamelogs_df['PREV_GAME_DATE'] = combined_gamelogs_df.groupby(['SEASON_YEAR', 'PLAYER_ID'])['GAME_DATE'].shift(1)
    
    # Calculate days, fill first game of season with 4, and cap at 8 to prevent injury outlier skew
    combined_gamelogs_df['DAYS_REST'] = (combined_gamelogs_df['GAME_DATE'] - combined_gamelogs_df['PREV_GAME_DATE']).dt.days
    combined_gamelogs_df['DAYS_REST'] = combined_gamelogs_df['DAYS_REST'].fillna(4).clip(upper=8).astype(int)
    combined_gamelogs_df = combined_gamelogs_df.drop(columns=['PREV_GAME_DATE'])

    # Usage Rate (USG%) & Team Pace Logic
    team_stats = combined_gamelogs_df.groupby(['GAME_ID', 'TEAM_ID'])[['FGA', 'FTA', 'TOV', 'MIN', 'OREB']].sum().reset_index()
    team_stats = team_stats.rename(columns={'FGA': 'TEAM_FGA', 'FTA': 'TEAM_FTA', 'TOV': 'TEAM_TOV', 'MIN': 'TEAM_MIN', 'OREB': 'TEAM_OREB'})
    
    team_stats['TEAM_EST_POSSESSIONS'] = team_stats['TEAM_FGA'] - team_stats['TEAM_OREB'] + team_stats['TEAM_TOV'] + (0.44 * team_stats['TEAM_FTA'])

    combined_gamelogs_df = combined_gamelogs_df.merge(team_stats, on=['GAME_ID', 'TEAM_ID'], how='left')
    
    numerator = (combined_gamelogs_df['FGA'] + 0.44 * combined_gamelogs_df['FTA'] + combined_gamelogs_df['TOV']) * (combined_gamelogs_df['TEAM_MIN'] / 5)
    denominator = combined_gamelogs_df['MIN'] * (combined_gamelogs_df['TEAM_FGA'] + 0.44 * combined_gamelogs_df['TEAM_FTA'] + combined_gamelogs_df['TEAM_TOV'])
    combined_gamelogs_df['USG_PCT'] = np.where(denominator > 0, (numerator / denominator) * 100, 0.0)
    combined_gamelogs_df['USG_PCT'] = combined_gamelogs_df['USG_PCT'].round(1)
    
    combined_gamelogs_df = combined_gamelogs_df.drop(columns=['TEAM_FGA', 'TEAM_FTA', 'TEAM_TOV', 'TEAM_MIN', 'TEAM_OREB'])

    # Drop unnecessary base columns
    columns_to_drop = [
        'NBA_FANTASY_PTS', 'DD2', 'TD3', 'WNBA_FANTASY_PTS', 'GP_RANK', 'W_RANK', 'L_RANK', 
        'W_PCT_RANK', 'MIN_RANK', 'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK', 
        'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK', 'OREB_RANK', 'DREB_RANK', 'REB_RANK', 
        'AST_RANK', 'TOV_RANK', 'STL_RANK', 'BLK_RANK', 'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 
        'PLUS_MINUS_RANK', 'NBA_FANTASY_PTS_RANK', 'DD2_RANK', 'TD3_RANK', 'WNBA_FANTASY_PTS_RANK', 
        'MIN_SEC', 'TEAM_COUNT', 'AVAILABLE_FLAG'
    ]
    existing_cols = [col for col in columns_to_drop if col in combined_gamelogs_df.columns]
    combined_gamelogs_df = combined_gamelogs_df.drop(columns=existing_cols)

    # Player Historical Stats & Efficiency
    combined_gamelogs_df = combined_gamelogs_df.sort_values(by=['PLAYER_ID', 'GAME_DATE'])
    
    # Season YTD Averages
    combined_gamelogs_df['PTS_SEASON_AVG'] = combined_gamelogs_df.groupby(['SEASON_YEAR', 'PLAYER_ID', 'TEAM_ID'])['PTS'].transform(lambda x: x.expanding().mean().shift(1)).round(1)
    combined_gamelogs_df['AST_SEASON_AVG'] = combined_gamelogs_df.groupby(['SEASON_YEAR', 'PLAYER_ID', 'TEAM_ID'])['AST'].transform(lambda x: x.expanding().mean().shift(1)).round(1)
    combined_gamelogs_df['REB_SEASON_AVG'] = combined_gamelogs_df.groupby(['SEASON_YEAR', 'PLAYER_ID', 'TEAM_ID'])['REB'].transform(lambda x: x.expanding().mean().shift(1)).round(1)
    combined_gamelogs_df['MIN_SEASON_AVG'] = combined_gamelogs_df.groupby(['SEASON_YEAR', 'PLAYER_ID', 'TEAM_ID'])['MIN'].transform(lambda x: x.expanding().mean().shift(1)).round(1)
    combined_gamelogs_df['USG_SEASON_AVG'] = combined_gamelogs_df.groupby(['SEASON_YEAR', 'PLAYER_ID', 'TEAM_ID'])['USG_PCT'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    
    # 10-Game Baselines
    combined_gamelogs_df['PTS_10G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['PTS'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['AST_10G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['AST'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['REB_10G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['REB'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['MIN_10G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['MIN'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['USG_10G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['USG_PCT'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    
    # Opportunity & Hot Streak Trackers
    combined_gamelogs_df['PTS_3G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['PTS'].transform(lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['AST_3G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['AST'].transform(lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['REB_3G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['REB'].transform(lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['MIN_3G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['MIN'].transform(lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)).round(1)
    combined_gamelogs_df['USG_3G_AVG'] = combined_gamelogs_df.groupby(['PLAYER_ID', 'TEAM_ID'])['USG_PCT'].transform(lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)).round(1)

    # Efficiency
    combined_gamelogs_df['TS_PCT'] = (combined_gamelogs_df['PTS'] / (2 * (combined_gamelogs_df['FGA'] + 0.44 * combined_gamelogs_df['FTA']))).fillna(0).round(3)
    combined_gamelogs_df['AST_TOV_RATIO'] = (combined_gamelogs_df['AST'] / (combined_gamelogs_df['TOV'] + 0.1)).round(2)

    # Opponent Rest Logic (FIXED SEASON CONTINUITY)
    # Ensure SEASON_YEAR is pulled so we can group by it
    team_dates = combined_gamelogs_df[['SEASON_YEAR', 'TEAM_ABBREVIATION', 'GAME_ID', 'GAME_DATE']].drop_duplicates()
    team_dates = team_dates.sort_values(['TEAM_ABBREVIATION', 'GAME_DATE'])
    
    # Group by Season AND Team
    team_dates['TEAM_PREV_GAME'] = team_dates.groupby(['SEASON_YEAR', 'TEAM_ABBREVIATION'])['GAME_DATE'].shift(1)
    
    # Calculate, fill with 4, and cap at 8 days
    team_dates['OPP_DAYS_REST'] = (team_dates['GAME_DATE'] - team_dates['TEAM_PREV_GAME']).dt.days
    team_dates['OPP_DAYS_REST'] = team_dates['OPP_DAYS_REST'].fillna(4).clip(upper=8).astype(int)
    
    team_rest_df = team_dates[['GAME_ID', 'TEAM_ABBREVIATION', 'OPP_DAYS_REST']].rename(columns={'TEAM_ABBREVIATION': 'OPPONENT'})
    combined_gamelogs_df = combined_gamelogs_df.merge(team_rest_df, on=['GAME_ID', 'OPPONENT'], how='left')

    # Opponent Defensive, Shooting & Pace Metrics Logic
    team_game_totals = combined_gamelogs_df.groupby(['GAME_ID', 'GAME_DATE', 'TEAM_ABBREVIATION', 'OPPONENT'])[['PTS', 'AST', 'REB', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTA', 'TOV', 'STL', 'BLK', 'OREB']].sum().reset_index()

    defensive_stats = team_game_totals.rename(columns={
        'OPPONENT': 'DEFENDING_TEAM',
        'PTS': 'PTS_ALLOWED', 'AST': 'AST_ALLOWED', 'REB': 'REB_ALLOWED',
        'FGM': 'FGM_ALLOWED', 'FGA': 'FGA_ALLOWED', 'FG3M': 'FG3M_ALLOWED', 
        'FG3A': 'FG3A_ALLOWED', 'FTA': 'FTA_ALLOWED', 'TOV': 'TOV_ALLOWED',
        'STL': 'STL_ALLOWED', 'BLK': 'BLK_ALLOWED', 'OREB': 'OREB_ALLOWED'
    })

    defensive_stats = defensive_stats.sort_values(by=['DEFENDING_TEAM', 'GAME_DATE'])
    
    defensive_stats['OPP_EST_POSSESSIONS'] = defensive_stats['FGA_ALLOWED'] - defensive_stats['OREB_ALLOWED'] + defensive_stats['TOV_ALLOWED'] + (0.44 * defensive_stats['FTA_ALLOWED'])

    rolling_opp = defensive_stats.groupby('DEFENDING_TEAM').rolling(window=10, min_periods=1)

    opp_pts_10g = rolling_opp['PTS_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_fga_10g = rolling_opp['FGA_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_fta_10g = rolling_opp['FTA_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_ast_10g = rolling_opp['AST_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_tov_10g = rolling_opp['TOV_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_fgm_10g = rolling_opp['FGM_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_fg3m_10g = rolling_opp['FG3M_ALLOWED'].sum().shift(1).reset_index(0, drop=True)
    opp_fg3a_10g = rolling_opp['FG3A_ALLOWED'].sum().shift(1).reset_index(0, drop=True)

    defensive_stats['OPP_TS_PCT_ALLOWED_10G'] = (opp_pts_10g / (2 * (opp_fga_10g + 0.44 * opp_fta_10g))).fillna(0).round(3)
    defensive_stats['OPP_AST_TOV_RATIO_ALLOWED_10G'] = (opp_ast_10g / (opp_tov_10g + 0.1)).fillna(0).round(2)
    defensive_stats['OPP_FG_PCT_ALLOWED_10G'] = (opp_fgm_10g / opp_fga_10g).fillna(0).round(3)
    defensive_stats['OPP_FG3_PCT_ALLOWED_10G'] = (opp_fg3m_10g / opp_fg3a_10g).fillna(0).round(3)

    defensive_stats['OPP_PTS_ALLOWED_10G'] = defensive_stats.groupby('DEFENDING_TEAM')['PTS_ALLOWED'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    defensive_stats['OPP_AST_ALLOWED_10G'] = defensive_stats.groupby('DEFENDING_TEAM')['AST_ALLOWED'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    defensive_stats['OPP_REB_ALLOWED_10G'] = defensive_stats.groupby('DEFENDING_TEAM')['REB_ALLOWED'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    defensive_stats['OPP_STL_ALLOWED_10G'] = defensive_stats.groupby('DEFENDING_TEAM')['STL_ALLOWED'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    defensive_stats['OPP_BLK_ALLOWED_10G'] = defensive_stats.groupby('DEFENDING_TEAM')['BLK_ALLOWED'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)
    
    defensive_stats['OPP_PACE_10G'] = defensive_stats.groupby('DEFENDING_TEAM')['OPP_EST_POSSESSIONS'].transform(lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)).round(1)

    cols_to_keep = [
        'GAME_ID', 'DEFENDING_TEAM', 'OPP_PTS_ALLOWED_10G', 'OPP_AST_ALLOWED_10G', 
        'OPP_REB_ALLOWED_10G', 'OPP_FG_PCT_ALLOWED_10G', 'OPP_FG3_PCT_ALLOWED_10G',
        'OPP_TS_PCT_ALLOWED_10G', 'OPP_AST_TOV_RATIO_ALLOWED_10G',
        'OPP_STL_ALLOWED_10G', 'OPP_BLK_ALLOWED_10G', 'OPP_PACE_10G'
    ]

    combined_gamelogs_df = combined_gamelogs_df.merge(
        defensive_stats[cols_to_keep], 
        left_on=['GAME_ID', 'OPPONENT'], 
        right_on=['GAME_ID', 'DEFENDING_TEAM'], 
        how='left'
    ).drop(columns=['DEFENDING_TEAM'])
    
    # Rest advantage logic
    combined_gamelogs_df['REST_DIFF'] = combined_gamelogs_df['DAYS_REST'] - combined_gamelogs_df['OPP_DAYS_REST']

    # Final Sort and Export
    combined_gamelogs_df = combined_gamelogs_df.sort_values(by=['GAME_DATE'], ascending=False)
    combined_gamelogs_df.to_csv('nba_master_gamelogs.csv', index=False)
    print(f"{len(combined_gamelogs_df)} total records saved.")

else:
    print("Process failed. No data was returned from the API.")
    
# More data analysis
df = combined_gamelogs_df

# --- 1: Correlation Heatmap ---
# Selecting key numeric columns to see how they interact
numeric_cols = ['MIN', 'PTS', 'AST', 'REB', 'USG_PCT', 'TS_PCT', 'PLUS_MINUS', 'DAYS_REST', 'TEAM_EST_POSSESSIONS']

plt.figure(figsize=(10, 8))
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap of Key Metrics')
plt.tight_layout()
plt.savefig('correlation_heatmap.png')
plt.close()

# --- 2: Usage vs Points (by Win/Loss) ---
plot_df_prelim2 = df.dropna(subset=['USG_PCT', 'PTS', 'WL']).sample(min(5000, len(df)), random_state=42)
fig_prelim2 = px.scatter(
    plot_df_prelim2, 
    x='USG_PCT', 
    y='PTS', 
    color='WL',
    hover_name='PLAYER_NAME',
    hover_data=['GAME_DATE', 'MATCHUP', 'MIN'],
    title='Usage Percentage vs. Points Scored',
    labels={'USG_PCT': 'Usage Percentage', 'PTS': 'Points Scored'},
    color_discrete_map={'W':'#2ecc71', 'L':'#e74c3c'},
    opacity=0.6
)
fig_prelim2.write_html('usage_vs_pts.html')

# --- 3: True Shooting vs. Usage Rate ---
plot_df1 = df[(df['MIN'] > 15) & df['USG_PCT'].notnull() & df['TS_PCT'].notnull()].sample(min(5000, len(df)), random_state=42)
fig1 = px.scatter(
    plot_df1, 
    x='USG_PCT', 
    y='TS_PCT', 
    size='MIN', 
    color='MIN',
    hover_name='PLAYER_NAME',
    hover_data=['GAME_DATE', 'MATCHUP', 'PTS', 'MIN'],
    title='Player Efficiency (TS% vs USG%)',
    labels={'USG_PCT': 'Usage Percentage', 'TS_PCT': 'True Shooting Percentage'},
    color_continuous_scale='viridis',
    opacity=0.7
)
fig1.write_html('ts_vs_usg.html')

# --- 4: Plus/Minus by Rest Diff ---
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='REST_DIFF', y='PLUS_MINUS', palette='coolwarm')
plt.title('Plus/Minus by Rest Differential')
plt.xlabel('Rest Differential (Player Rest - Opponent Rest in Days)')
plt.ylabel('Player Plus/Minus')
plt.axhline(0, color='black', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('rest_advantage.png')
plt.close()

# --- 5: Opponent Defense vs Points Scored ---
plot_df4 = df.dropna(subset=['OPP_PTS_ALLOWED_10G', 'PTS']).sample(min(5000, len(df)), random_state=42)
fig4 = px.scatter(
    plot_df4, 
    x='OPP_PTS_ALLOWED_10G', 
    y='PTS', 
    hover_name='PLAYER_NAME',
    hover_data=['GAME_DATE', 'MATCHUP', 'MIN'],
    trendline='ols', # Adds the ordinary least squares regression line
    trendline_color_override='black',
    title='Matchup Impact (Opponent Defense vs. Points Scored)',
    labels={'OPP_PTS_ALLOWED_10G': 'Opponent Average Pts Allowed (Last 10G)', 'PTS': 'Actual Points Scored'},
    color_discrete_sequence=['purple'],
    opacity=0.4
)
fig4.write_html('opp_defense_vs_pts.html')

# --- 6: Opponent Pace vs Player Stats ---
plot_df5 = df.dropna(subset=['OPP_PACE_10G', 'PTS']).sample(min(5000, len(df)), random_state=42)
fig5 = px.scatter(
    plot_df5, 
    x='OPP_PACE_10G', 
    y='PTS', 
    hover_name='PLAYER_NAME',
    hover_data=['GAME_DATE', 'MATCHUP', 'MIN'],
    trendline='ols', # Adds the ordinary least squares regression line
    trendline_color_override='blue',
    title='Opponent Pace vs. Points Scored',
    labels={'OPP_PACE_10G': 'Opponent 10-Game Pace', 'PTS': 'Points Scored'},
    color_discrete_sequence=['gray'],
    opacity=0.4
)
fig5.write_html('pace_vs_pts.html')

# --- 7: Playoff Minutes Distribution ---
plt.figure(figsize=(9, 6))
df_playoff = df.copy()
df_playoff['SEASON_TYPE'] = df_playoff['IS_PLAYOFF'].map({0: 'Regular Season', 1: 'Playoffs'})
df_rotation = df_playoff[df_playoff['MIN'] > 10]

sns.violinplot(data=df_rotation.dropna(subset=['SEASON_TYPE', 'MIN']), 
               x='SEASON_TYPE', y='MIN', palette=['#3498db', '#e74c3c'], inner='quartile')
plt.title('Minutes Distribution: Regular Season vs Playoffs (Rotation Players)')
plt.ylabel('Minutes Played')
plt.xlabel('')
plt.tight_layout()
plt.savefig('playoff_minutes.png')
plt.close()

# --- 8: Diminishing Returns of Usage ---
plt.figure(figsize=(10, 8))
plot_df8 = df[(df['MIN'] > 10) & df['USG_PCT'].notnull() & df['TS_PCT'].notnull()]
hb = plt.hexbin(plot_df8['USG_PCT'], plot_df8['TS_PCT'], gridsize=40, cmap='inferno', mincnt=1)
cb = plt.colorbar(hb, label='Number of Games')
plt.xlabel('Usage Percentage (USG_PCT)')
plt.ylabel('True Shooting Percentage (TS_PCT)')
plt.title('Density of Usage vs True Shooting')
plt.tight_layout()
plt.savefig('usage_hexbin.png')
plt.close()

# --- 9: Tracking "Hot" and "Cold" Streaks ---
top_player = df.groupby('PLAYER_NAME')['PTS'].sum().idxmax()
player_df = df[df['PLAYER_NAME'] == top_player].sort_values('GAME_DATE').copy()
player_df['PTS_DIFF'] = player_df['PTS_10G_AVG'] - player_df['PTS_SEASON_AVG']
player_df = player_df.dropna(subset=['GAME_DATE', 'PTS_DIFF'])

plt.figure(figsize=(12, 6))
x = np.arange(len(player_df))
y = player_df['PTS_DIFF'].values

plt.fill_between(x, y, 0, where=(y >= 0), color='mediumseagreen', alpha=0.6, interpolate=True, label='Hot Streak (Above Avg)')
plt.fill_between(x, y, 0, where=(y < 0), color='indianred', alpha=0.6, interpolate=True, label='Cold Streak (Below Avg)')
plt.plot(x, y, color='black', linewidth=1.5, alpha=0.8)
plt.axhline(0, color='black', linestyle='--', linewidth=1)

plt.title(f'{top_player}: Form Tracker (10-Game Avg vs Season Avg)')
plt.xlabel('Games Played (Chronological)')
plt.ylabel('Points Differential (10G Avg - Season Avg)')
plt.legend()
plt.tight_layout()
plt.savefig('hot_cold_streaks.png')
plt.close()

# --- Model Development
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

targets = ['PTS', 'REB', 'AST']
non_numeric_cols = train_df.select_dtypes(exclude=['number']).columns.tolist()

# In-game stats that leak data
drop_num_cols = [
    'PLAYER_ID', 'TEAM_ID', 'GAME_ID', 'GAME_DATE',
    'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 
    'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 
    'PF', 'PFD', 'PTS', 'PLUS_MINUS', 'USG_PCT', 'TS_PCT', 'AST_TOV_RATIO'
]

drop_cols = list(set(drop_num_cols + non_numeric_cols))

# Training models
models = {}
for target in targets:
    # Define y
    y_train = train_df[target]
    y_test = test_df[target]
    
    # Define X
    X_train = train_df.drop(columns=drop_cols, errors='ignore')
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    
    # Handle NaNs with SimpleImputer
    imputer = SimpleImputer(strategy='median')
    
    # Fit on train, transform both train and test. 
    X_train_imputed = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
    X_test_imputed = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)
    
    # Initialize and fit the model
    model = LassoCV(cv=5, random_state=42)
    model.fit(X_train_imputed, y_train)
    
    # Evaluate using the imputed data
    train_preds = model.predict(X_train_imputed)
    test_preds = model.predict(X_test_imputed)
    
    rmse = np.sqrt(mean_squared_error(y_test, test_preds))
    mae = mean_absolute_error(y_test, test_preds)
    
    print(f"Test RMSE: {rmse:.2f} {target} | Test MAE: {mae:.2f} {target}")
    
    # Show Top Features
    feature_importance = pd.DataFrame({
        'Feature': X_train_imputed.columns,
        'Coefficient': model.coef_
    }).sort_values(by='Coefficient', key=abs, ascending=False)
    
    print(f"Top 3 Features for {target}:")
    print(feature_importance[feature_importance['Coefficient'] != 0].head(3).to_string(index=False))
    
    # Save the model to our dictionary
    models[target] = model

# Generate matchup based predictions
df_sorted = df.sort_values('GAME_DATE')
latest_players = df_sorted.groupby('PLAYER_NAME').tail(1).copy()
opp_cols = [c for c in df.columns if c.startswith('OPP_') or c == 'OPPONENT']
latest_players = latest_players.drop(columns=opp_cols, errors='ignore')
latest_defense = df_sorted.groupby('OPPONENT').tail(1)[opp_cols].copy()

latest_players['cross_key'] = 1
latest_defense['cross_key'] = 1
future_matchups = pd.merge(latest_players, latest_defense, on='cross_key').drop('cross_key', axis=1)

# Remove matchups where a player is scheduled to play against their own team
if 'TEAM_ABBREVIATION' in future_matchups.columns:
    future_matchups = future_matchups[future_matchups['TEAM_ABBREVIATION'] != future_matchups['OPPONENT']]

# Hardcode opponent and site characteristics for now
if 'IS_HOME' in future_matchups.columns:
    future_matchups['IS_HOME'] = 0.5  # Neutral court assumption
if 'DAYS_REST' in future_matchups.columns:
    future_matchups['DAYS_REST'] = 2.0 # Standard league average rest
if 'OPP_DAYS_REST' in future_matchups.columns:
    future_matchups['OPP_DAYS_REST'] = 2.0
if 'REST_DIFF' in future_matchups.columns:
    future_matchups['REST_DIFF'] = 0.0

# Prepare the feature set
X_future = future_matchups.drop(columns=drop_cols, errors='ignore')

# Reorder columns to match the training data
X_future = X_future[X_train.columns]

# Impute NaNs using the last imputer state
X_future_imputed = pd.DataFrame(imputer.transform(X_future), columns=X_future.columns)

# Generate Predictions for each target using the saved models
for target in targets:
    model = models[target]
    future_matchups[f'PROJ_{target}'] = np.round(model.predict(X_future_imputed), 1)

# Clean up and display the final projections
final_cols = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'OPPONENT'] + [f'PROJ_{t}' for t in targets]

# Make sure all final columns actually exist in the dataframe before selecting them
final_cols = [c for c in final_cols if c in future_matchups.columns]
final_projections = future_matchups[final_cols].sort_values(by=['PLAYER_NAME', 'OPPONENT'])

print("\nProjections generated! Here is a sample for the first player:")
print(final_projections.head())

# Save to CSV
final_projections.to_csv('all_matchups_projections.csv', index=False)