DROP DATABASE IF EXISTS prediction_modeldb;
CREATE DATABASE prediction_modeldb;
USE prediction_modeldb;

DROP TABLE IF EXISTS raw_player_game_logs;

CREATE TABLE raw_player_game_logs (
    -- Primary Key
    game_log_id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Identifiers & Dimensions
    season_year VARCHAR(10),        -- e.g., '2024-25'
    player_id INT,                  -- e.g., 2544
    player_name VARCHAR(100),       -- e.g., 'LeBron James'
    team_id BIGINT,                 -- e.g., 1610612747
    team_abbreviation VARCHAR(10),  -- e.g., 'LAL'
    team_name VARCHAR(100),         -- e.g., 'Los Angeles Lakers'
    game_id VARCHAR(20),            -- e.g., '0022400001' (needs varchar for leading zeros)
    game_date DATE,                 -- e.g., '2024-10-22'
    matchup VARCHAR(30),            -- e.g., 'LAL vs. MIN'
    wl VARCHAR(5),                  -- e.g., 'W' or 'L'
    
    -- Minutes & Percentages (Decimals)
    min DOUBLE,
    fg_pct DOUBLE,
    fg3_pct DOUBLE,
    ft_pct DOUBLE,
    
    -- Core Counting Stats (Integers)
    fgm INT,
    fga INT,
    fg3m INT,
    fg3a INT,
    ftm INT,
    fta INT,
    oreb INT,
    dreb INT,
    reb INT,
    ast INT,
    tov INT,
    stl INT,
    blk INT,
    blka INT,
    pf INT,
    pfd INT,
    pts INT,
    plus_minus INT,
    available_flag INT,
    
    -- Performance Indexes (Speeds up the pandas retrieval later)
    INDEX idx_player_date (player_id, game_date),
    INDEX idx_team_game (team_id, game_id),
    INDEX idx_game_date (game_date)
);

DROP TABLE IF EXISTS matchup_projections;

CREATE TABLE matchup_projections (
    player_name VARCHAR(100),
    team_abbreviation VARCHAR(10),
    opponent VARCHAR(10),
    pred_points DOUBLE,
    pred_rebounds DOUBLE,
    pred_assists DOUBLE,
    pred_pra DOUBLE,
    
    -- Composite Primary Key allows a player to have multiple rows 
    -- as long as the opponent is different
    PRIMARY KEY (player_name, opponent)
);

DROP TABLE IF EXISTS player_aggregates;

CREATE TABLE player_aggregates (
    -- Identifiers
    player_id INT PRIMARY KEY,
    player_name VARCHAR(100),
    
    -- Points Aggregates
    last_3_points DOUBLE,
    last_5_points DOUBLE,
    last_10_points DOUBLE,
    season_avg_points DOUBLE,
    
    -- Rebounds Aggregates
    last_3_rebounds DOUBLE,
    last_5_rebounds DOUBLE,
    last_10_rebounds DOUBLE,
    season_avg_rebounds DOUBLE,
    
    -- Assists Aggregates
    last_3_assists DOUBLE,
    last_5_assists DOUBLE,
    last_10_assists DOUBLE,
    season_avg_assists DOUBLE
);