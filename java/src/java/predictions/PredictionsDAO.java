/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package predictions;

/**
 *
 * @author 1zomb
 */

import predictions.DBConnection;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import predictions.MergeSort;
import predictions.DBConnection;
import predictions.MergeSort;
import predictions.Prediction;

public class PredictionsDAO {
    public ArrayList<Prediction> getAllPredictions() {
        ArrayList<Prediction> predictions = new ArrayList<>();

        String sql = "SELECT player_name, team_abbreviation, opponent, " +
        "pred_points, pred_rebounds, pred_assists, pred_pra " +
        "FROM matchup_projections";

   

        try (
            Connection conn = DBConnection.getConnection();
            PreparedStatement stmt = conn.prepareStatement(sql);
            ResultSet rs = stmt.executeQuery()
        ) {
            while (rs.next()) {
                String playerName = rs.getString("player_name");
                String opponent = rs.getString("opponent");
                String team_abbreviation = rs.getString("team_abbreviation");
                double predPoints = rs.getDouble("pred_points");
                double predRebounds = rs.getDouble("pred_rebounds");
                double predAssists = rs.getDouble("pred_assists");
                double predPRA = rs.getDouble("pred_pra");

                Prediction prediction = new Prediction(
                        playerName, opponent,team_abbreviation, predPoints, predRebounds, predAssists, predPRA
                );

                predictions.add(prediction);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }

        return predictions;
    }
    public ArrayList<Prediction> getPredictionsForGame(String team1, String team2) {
    ArrayList<Prediction> predictions = new ArrayList<>();

    String sql =  "SELECT mp.player_name, mp.team_abbreviation, mp.opponent, " +
    "mp.pred_points, mp.pred_rebounds, mp.pred_assists, mp.pred_pra, " +
    "pa.last_5_points, pa.last_5_rebounds, pa.last_5_assists " +
    "FROM matchup_projections mp " +
    "LEFT JOIN player_aggregates pa " +
    "ON mp.player_name = pa.player_name " +
    "WHERE (mp.team_abbreviation = ? AND mp.opponent = ?) " +
    "OR (mp.team_abbreviation = ? AND mp.opponent = ?)";

    try (
        Connection conn = DBConnection.getConnection();
        PreparedStatement stmt = conn.prepareStatement(sql)
    ) {
        stmt.setString(1, team1);
        stmt.setString(2, team2);
        stmt.setString(3, team2);
        stmt.setString(4, team1);

        ResultSet rs = stmt.executeQuery();

        while (rs.next()) {

    Prediction prediction = new Prediction(
        rs.getString("player_name"),
        rs.getString("opponent"),
        rs.getString("team_abbreviation"),
        rs.getDouble("pred_points"),
        rs.getDouble("pred_rebounds"),
        rs.getDouble("pred_assists"),
        rs.getDouble("pred_pra")
    );

    prediction.setLast5Points(rs.getDouble("last_5_points"));
    prediction.setLast5Rebounds(rs.getDouble("last_5_rebounds"));
    prediction.setLast5Assists(rs.getDouble("last_5_assists"));

    predictions.add(prediction);
}

    } catch (SQLException e) {
        e.printStackTrace();
    }

    return predictions;
}
  public ArrayList<Prediction> getPredictionsForSlate(String[][] slate) {
   ArrayList<Prediction> allPredictions = new ArrayList<>();

    for (String[] game : slate) {
        String team1 = game[0];
        String team2 = game[1];

        allPredictions.addAll(getPredictionsForGame(team1, team2));
    }

    MergeSort sorter = new MergeSort();
    allPredictions = new ArrayList<>(sorter.mergeSort(allPredictions, "pra"));

    return allPredictions;  
    
}
  public ArrayList<String> getTeams() {
    ArrayList<String> teams = new ArrayList<>();
    String sql = "SELECT DISTINCT team_abbreviation FROM matchup_projections";

    try (Connection conn = DBConnection.getConnection();
         PreparedStatement stmt = conn.prepareStatement(sql);
         ResultSet rs = stmt.executeQuery()) {

        while (rs.next()) {
            teams.add(rs.getString("team_abbreviation"));
        }
    } catch (SQLException e) { e.printStackTrace(); }

    return teams;
}

public ArrayList<String> getMatchups() {
    ArrayList<String> matchups = new ArrayList<>();
    String sql = "SELECT DISTINCT team_abbreviation, opponent FROM matchup_projections";

    try (Connection conn = DBConnection.getConnection();
         PreparedStatement stmt = conn.prepareStatement(sql);
         ResultSet rs = stmt.executeQuery()) {

        while (rs.next()) {
            matchups.add(rs.getString("team_abbreviation") + " @ " + rs.getString("opponent"));
        }
    } catch (SQLException e) { e.printStackTrace(); }

    return matchups;
}
  
}