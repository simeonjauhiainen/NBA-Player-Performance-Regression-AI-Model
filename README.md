# NBA Player Prediction Model

## Overview
This project predicts NBA player performance (points, rebounds, assists) using real game data.

It is built as a simple data pipeline:
- Python collects and processes data
- MySQL stores the data
- Java (JDBC) retrieves and displays predictions

## Tech Stack
- Python
- MySQL
- Java (JDBC)
- Pandas
- nba_api

## How It Works
1. Pull NBA game logs using nba_api
2. Clean and store data in MySQL
3. Calculate recent performance (last 5 games)
4. Java backend queries the database
5. Output player projections

## Features
- Stores multi-season NBA player data
- Handles missing data (NaN to NULL)
- Calculates averages for points, rebounds, assists
- Supports filtering by team, matchup, and date

## Example Query
```sql
SELECT player_id,
       AVG(pts) AS avg_pts,
       AVG(reb) AS avg_reb,
       AVG(ast) AS avg_ast
FROM (
    SELECT *
    FROM player_game_logs
    WHERE player_id = ?
    ORDER BY game_date DESC
    LIMIT 5
) AS last5;
