package predictions;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

public class PredictionsDAO {

    public ArrayList<Prediction> getAllPredictions() {
        ArrayList<Prediction> predictions = new ArrayList<>();
        String sql = "SELECT player_name, team_abbreviation, opponent, "
                + "pred_points, pred_rebounds, pred_assists, pred_pra "
                + "FROM matchup_projections";

        try (
                Connection conn = DBConnection.getConnection(); PreparedStatement stmt = conn.prepareStatement(sql); ResultSet rs = stmt.executeQuery()) {
            while (rs.next()) {
                Prediction prediction = new Prediction(
                        rs.getString("player_name"), rs.getString("opponent"), rs.getString("team_abbreviation"),
                        rs.getDouble("pred_points"), rs.getDouble("pred_rebounds"), rs.getDouble("pred_assists"), rs.getDouble("pred_pra")
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

        String sql = "SELECT mp.player_name, mp.team_abbreviation, mp.opponent, "
                + "mp.pred_points, mp.pred_rebounds, mp.pred_assists, mp.pred_pra, "
                + "pa.last_3_points, pa.last_3_rebounds, pa.last_3_assists, "
                + "pa.last_5_points, pa.last_5_rebounds, pa.last_5_assists, "
                + "pa.last_10_points, pa.last_10_rebounds, pa.last_10_assists, "
                + "pa.season_avg_points, pa.season_avg_rebounds, pa.season_avg_assists "
                + "FROM matchup_projections mp "
                + "LEFT JOIN player_aggregates pa "
                + "ON mp.player_name = pa.player_name "
                + "WHERE (mp.team_abbreviation = ? AND mp.opponent = ?) "
                + "OR (mp.team_abbreviation = ? AND mp.opponent = ?)";

        try (
                Connection conn = DBConnection.getConnection(); PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, team1);
            stmt.setString(2, team2);
            stmt.setString(3, team2);
            stmt.setString(4, team1);
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                Prediction prediction = new Prediction(
                        rs.getString("player_name"), rs.getString("opponent"), rs.getString("team_abbreviation"),
                        rs.getDouble("pred_points"), rs.getDouble("pred_rebounds"), rs.getDouble("pred_assists"), rs.getDouble("pred_pra")
                );

                // Grab Last 3
                prediction.setLast3Points(rs.getDouble("last_3_points"));
                prediction.setLast3Rebounds(rs.getDouble("last_3_rebounds"));
                prediction.setLast3Assists(rs.getDouble("last_3_assists"));

                // Grab Last 5
                prediction.setLast5Points(rs.getDouble("last_5_points"));
                prediction.setLast5Rebounds(rs.getDouble("last_5_rebounds"));
                prediction.setLast5Assists(rs.getDouble("last_5_assists"));

                // Grab Last 10
                prediction.setLast10Points(rs.getDouble("last_10_points"));
                prediction.setLast10Rebounds(rs.getDouble("last_10_rebounds"));
                prediction.setLast10Assists(rs.getDouble("last_10_assists"));

                // Grab Season Averages
                prediction.setSeasonPoints(rs.getDouble("season_avg_points"));
                prediction.setSeasonRebounds(rs.getDouble("season_avg_rebounds"));
                prediction.setSeasonAssists(rs.getDouble("season_avg_assists"));

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
        return new ArrayList<>(sorter.mergeSort(allPredictions, "pra"));
    }

    public ArrayList<String> getTeams() {
        ArrayList<String> teams = new ArrayList<>();
        String sql = "SELECT DISTINCT team_abbreviation FROM matchup_projections";
        try (Connection conn = DBConnection.getConnection(); PreparedStatement stmt = conn.prepareStatement(sql); ResultSet rs = stmt.executeQuery()) {
            while (rs.next()) {
                teams.add(rs.getString("team_abbreviation"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return teams;
    }

    public ArrayList<String> getMatchups() {
        ArrayList<String> matchups = new ArrayList<>();
        String sql = "SELECT DISTINCT team_abbreviation, opponent FROM matchup_projections";
        try (Connection conn = DBConnection.getConnection(); PreparedStatement stmt = conn.prepareStatement(sql); ResultSet rs = stmt.executeQuery()) {
            while (rs.next()) {
                matchups.add(rs.getString("team_abbreviation") + " @ " + rs.getString("opponent"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return matchups;
    }
}
