DROP DATABASE IF EXISTS prediction_modeldb;
CREATE DATABASE prediction_modeldb;
USE prediction_modeldb;

-- =========================
-- Players
-- =========================
CREATE TABLE players (
    player_id INT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    team_abbreviation VARCHAR(10)
);

-- =========================
-- Player Game Logs
-- =========================
CREATE TABLE player_game_logs (
    game_log_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    team_id INT,
    team_abbreviation VARCHAR(10),
    game_id VARCHAR(20) NOT NULL,
    game_date DATE NOT NULL,
    matchup VARCHAR(20),
    wl VARCHAR(5),
    `min` DECIMAL(6,2),
    pts INT,
    reb INT,
    ast INT,
    stl INT,
    blk INT,
    tov INT,
    fgm INT,
    fga INT,
    fg3m INT,
    fg3a INT,
    ftm INT,
    fta INT,
    oreb INT,
    dreb INT,
    pf INT,
    plus_minus INT,
    season_queried VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_player_game_logs_player
        FOREIGN KEY (player_id)
        REFERENCES players(player_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_player_game
        UNIQUE (player_id, game_id)
);

-- =========================
-- Player Aggregates
-- =========================
CREATE TABLE player_aggregates (
    aggregate_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    slate_date DATE,
    last_5_fp DECIMAL(8,2),
    season_fp DECIMAL(8,2),
    last_5_minutes DECIMAL(8,2),
    last_10_minutes DECIMAL(8,2),
    last_5_points DECIMAL(8,2),
    last_10_points DECIMAL(8,2),
    last_5_rebounds DECIMAL(8,2),
    last_10_rebounds DECIMAL(8,2),
    last_5_assists DECIMAL(8,2),
    last_10_assists DECIMAL(8,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_player_aggregates_player
        FOREIGN KEY (player_id)
        REFERENCES players(player_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_player_aggregate
        UNIQUE (player_id)
);

-- =========================
-- Matchup Projections
-- =========================
CREATE TABLE matchup_projections (
    projection_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    team_abbreviation VARCHAR(10),
    opponent VARCHAR(10),
    pred_points DECIMAL(5,2),
    pred_rebounds DECIMAL(5,2),
    pred_assists DECIMAL(5,2),
    pred_pra DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);