# 🏀 NBA Player Prediction Model

## Overview
This project is an end-to-end data pipeline and prediction engine designed to forecast NBA player performance—specifically Points (PTS), Rebounds (REB), and Assists (AST)—using real, historical game data. 

Rather than relying on manual spreadsheet tracking, this system automates the entire process: extracting data from the NBA's official endpoints, cleaning and storing it in a relational database, and serving calculated projections through a Java backend. It currently utilizes a rolling-average model (e.g., Last 5 Games) to project near-term performance.

## Tech Stack
*   **Data Collection & Processing:** Python 3, Pandas, `nba_api`
*   **Database:** MySQL
*   **Backend & Data Serving:** Java (JDBC)

---

## 📊 Model Accuracy Results

*Note: Replace these placeholder metrics with your model's actual testing results.*

To evaluate the effectiveness of the projections, the model's predictions were tested against a holdout dataset of actual NBA games. Performance is measured using **Mean Absolute Error (MAE)**, which represents the average difference between the predicted stat line and the actual game result.

### Overall Error Margins (Last 5 Games Moving Average)
| Stat Category | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) |
| :--- | :--- | :--- |
| **Points (PTS)** | ± 4.2 | 5.8 |
| **Rebounds (REB)** | ± 1.8 | 2.4 |
| **Assists (AST)** | ± 1.5 | 2.1 |

### Sample Prediction vs. Actuals
*Example based on a recent testing sample:*

| Player | Predicted PTS | Actual PTS | Error |
| :--- | :--- | :--- | :--- |
| **LeBron James** | 24.5 | 26 | -1.5 |
| **Nikola Jokic** | 28.2 | 27 | +1.2 |
| **Stephen Curry** | 29.0 | 22 | +7.0 |

---

## ⚙️ Architecture & Data Pipeline

The project follows a standard ETL (Extract, Transform, Load) architecture:

1.  **Extract:** Python scripts utilize the `nba_api` library to pull massive batches of raw player game logs directly from the NBA's statistical databases.
2.  **Transform:** The raw JSON data is loaded into Pandas DataFrames. Here, we handle missing data (converting NaNs to NULLs for SQL compatibility), filter out irrelevant exhibition games, and structure the data types.
3.  **Load:** Using Python's MySQL connector, the cleaned DataFrames are bulk-inserted into a structured MySQL database (`player_game_logs`).
4.  **Serve:** A Java backend establishes a JDBC connection to the MySQL database. It executes complex SQL queries to calculate real-time projections based on rolling averages (e.g., last 5 games) and serves them to the user.

## Features
*   **Multi-Season Tracking:** Capable of storing and querying thousands of game logs across multiple NBA seasons.
*   **Automated Data Cleaning:** Safely handles missing values, DNP (Did Not Play) designations, and data anomalies before database insertion.
*   **Dynamic Projections:** Calculates up-to-date averages for PTS, REB, and AST on the fly.
*   **Robust Filtering:** Supports querying by specific player IDs, opposing teams, matchups, and date ranges.

---

## Example Query: Generating a Projection

The Java application relies on SQL subqueries to generate predictions. Here is a query used to grab a player's stats from the last 5 games, which dictates recent form:

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
) AS last5_games;
