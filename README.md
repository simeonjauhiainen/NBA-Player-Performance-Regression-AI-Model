🏀 NBA DFS Prediction Model

Full-Stack Data Pipeline | Python + MySQL + Java

🚀 Overview

This project is an end-to-end NBA analytics pipeline that collects real game data, engineers predictive features, trains machine learning models, and serves player projections through a backend system.

Built to mirror real-world sports analytics workflows used in Daily Fantasy Sports (DFS) and data-driven decision systems.

🧱 Tech Stack

Data Engineering

Python (Pandas, NumPy)
nba_api

Machine Learning

Scikit-learn (Lasso Regression)

Database

MySQL

Backend

Java (JDBC)
Apache Tomcat
⚙️ System Architecture
NBA API → Python Pipeline → MySQL Database → Java Backend → Frontend (Dashboard)
🔥 Key Features
📊 Data Pipeline
Fetches multi-season NBA player game logs
Cleans and structures raw data
Loads into relational database
🧠 Feature Engineering
Rolling averages (last 5 / last 10 games)
Usage rate (USG%) and efficiency metrics
Opponent defensive statistics
Rest days and matchup-based features
🤖 Machine Learning
Predicts:
Points
Rebounds
Assists
Uses Lasso Regression for feature selection and performance
📈 Projection Engine
Generates matchup-based predictions for all players
Calculates PRA (Points + Rebounds + Assists)
Stores results in MySQL for querying
🔌 Backend Integration
Java connects to MySQL via JDBC
Retrieves projections and aggregates
Powers a web-based dashboard (in progress)
🗂️ Project Structure
nba-prediction-project/
│
├── python/
│   ├── db_connection.py
│   ├── nba_daily_stats.py
│   ├── load_game_logs.py
│   ├── player_aggregates.py
│   ├── model_training.py
│   └── load_matchup_projections.py
│
├── database/
│   ├── schema.sql
│   └── queries.sql
│
├── java/
│   └── (Java backend project)
│
└── sample_data/
▶️ How to Run
1. Setup Database
CREATE DATABASE prediction_modeldb;

Run schema.sql

2. Run Data Pipeline
python load_game_logs.py
python player_aggregates.py
python model_training.py
python load_matchup_projections.py
3. Run Java Backend
Connect using JDBC
Query matchup_projections table
📊 Example Output
Player projections (PTS, REB, AST, PRA)
Rolling performance metrics
Matchup-based insights
🧪 What This Project Demonstrates
End-to-end data pipeline design
Backend development with Java + SQL
Real-world machine learning workflow
Feature engineering for predictive modeling
Database integration across multiple layers
🔮 Future Improvements
Real-time data ingestion
Full frontend dashboard UI
Advanced models (XGBoost, ensembles)
DFS lineup optimizer
👤 Author

Computer Science Senior focused on backend development and data-driven systems
