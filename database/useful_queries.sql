USE prediction_modeldb;

-- =========================
-- View Top PRA Projections
-- =========================
SELECT
    player_name,
    team_abbreviation,
    opponent,
    pred_points,
    pred_rebounds,
    pred_assists,
    pred_pra
FROM matchup_projections
ORDER BY pred_pra DESC;

-- =========================
-- View Projections By Team
-- =========================
SELECT *
FROM matchup_projections
WHERE team_abbreviation = 'LAL'
ORDER BY pred_pra DESC;

-- =========================
-- View Projections By Opponent
-- =========================
SELECT *
FROM matchup_projections
WHERE opponent = 'OKC'
ORDER BY pred_pra DESC;

-- =========================
-- Search Player Projection
-- =========================
SELECT *
FROM matchup_projections
WHERE player_name LIKE '%LeBron%';

-- =========================
-- View Latest Game Logs
-- =========================
SELECT
    player_name,
    team_abbreviation,
    game_date,
    matchup,
    pts,
    reb,
    ast,
    `min`
FROM player_game_logs
ORDER BY game_date DESC
LIMIT 25;

-- =========================
-- View Player Game History
-- =========================
SELECT
    game_date,
    matchup,
    wl,
    pts,
    reb,
    ast,
    `min`
FROM player_game_logs
WHERE player_name = 'LeBron James'
ORDER BY game_date DESC;

-- =========================
-- View Player Aggregates
-- =========================
SELECT
    player_name,
    last_5_points,
    last_5_rebounds,
    last_5_assists,
    last_5_minutes,
    season_fp
FROM player_aggregates
ORDER BY season_fp DESC;

-- =========================
-- Join Players With Aggregates
-- =========================
SELECT
    p.player_name,
    p.team_abbreviation,
    a.last_5_points,
    a.last_5_rebounds,
    a.last_5_assists,
    a.last_5_minutes,
    a.season_fp
FROM players p
JOIN player_aggregates a
    ON p.player_id = a.player_id
ORDER BY a.season_fp DESC;

-- =========================
-- Check Row Counts
-- =========================
SELECT 'players' AS table_name, COUNT(*) AS total_rows FROM players
UNION ALL
SELECT 'player_game_logs', COUNT(*) FROM player_game_logs
UNION ALL
SELECT 'player_aggregates', COUNT(*) FROM player_aggregates
UNION ALL
SELECT 'matchup_projections', COUNT(*) FROM matchup_projections;

-- =========================
-- Check Duplicate Game Logs
-- =========================
SELECT
    player_id,
    game_id,
    COUNT(*) AS duplicate_count
FROM player_game_logs
GROUP BY player_id, game_id
HAVING COUNT(*) > 1;