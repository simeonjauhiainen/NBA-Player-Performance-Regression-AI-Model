package predictions;

public class Prediction {

    private String playerName;
    private String opponent;
    private String team_abbreviation;
    private double predPoints;
    private double predRebounds;
    private double predAssists;
    private double predPRA;

    // Aggregate stats
    private double last3Points, last3Rebounds, last3Assists;
    private double last5Points, last5Rebounds, last5Assists;
    private double last10Points, last10Rebounds, last10Assists;
    private double seasonPoints, seasonRebounds, seasonAssists;

    // Constructors
    public Prediction(String playerName, String opponent, String team_abbreviation, double predPoints,
            double predRebounds, double predAssists, double predPRA) {
        this.playerName = playerName;
        this.opponent = opponent;
        this.team_abbreviation = team_abbreviation;
        this.predPoints = predPoints;
        this.predRebounds = predRebounds;
        this.predAssists = predAssists;
        this.predPRA = predPRA;
    }

    public Prediction() {
    }

    // Getters
    public String getPlayerName() {
        return playerName;
    }

    public String getOpponent() {
        return opponent;
    }

    public String getTeam() {
        return team_abbreviation;
    }

    public double getPredPoints() {
        return predPoints;
    }

    public double getPredRebounds() {
        return predRebounds;
    }

    public double getPredAssists() {
        return predAssists;
    }

    public double getPredPRA() {
        return predPRA;
    }

    public double getLast3Points() {
        return last3Points;
    }

    public double getLast3Rebounds() {
        return last3Rebounds;
    }

    public double getLast3Assists() {
        return last3Assists;
    }

    public double getLast5Points() {
        return last5Points;
    }

    public double getLast5Rebounds() {
        return last5Rebounds;
    }

    public double getLast5Assists() {
        return last5Assists;
    }

    public double getLast10Points() {
        return last10Points;
    }

    public double getLast10Rebounds() {
        return last10Rebounds;
    }

    public double getLast10Assists() {
        return last10Assists;
    }

    public double getSeasonPoints() {
        return seasonPoints;
    }

    public double getSeasonRebounds() {
        return seasonRebounds;
    }

    public double getSeasonAssists() {
        return seasonAssists;
    }

    // Setters
    public void setPlayerName(String playerName) {
        this.playerName = playerName;
    }

    public void setOpponent(String opponent) {
        this.opponent = opponent;
    }

    public void setTeam_abbreviation(String team_abbreviation) {
        this.team_abbreviation = team_abbreviation;
    }

    public void setPredPoints(double predPoints) {
        this.predPoints = predPoints;
    }

    public void setPredRebounds(double predRebounds) {
        this.predRebounds = predRebounds;
    }

    public void setPredAssists(double predAssists) {
        this.predAssists = predAssists;
    }

    public void setPredPRA(double predPRA) {
        this.predPRA = predPRA;
    }

    public void setLast3Points(double last3Points) {
        this.last3Points = last3Points;
    }

    public void setLast3Rebounds(double last3Rebounds) {
        this.last3Rebounds = last3Rebounds;
    }

    public void setLast3Assists(double last3Assists) {
        this.last3Assists = last3Assists;
    }

    public void setLast5Points(double last5Points) {
        this.last5Points = last5Points;
    }

    public void setLast5Rebounds(double last5Rebounds) {
        this.last5Rebounds = last5Rebounds;
    }

    public void setLast5Assists(double last5Assists) {
        this.last5Assists = last5Assists;
    }

    public void setLast10Points(double last10Points) {
        this.last10Points = last10Points;
    }

    public void setLast10Rebounds(double last10Rebounds) {
        this.last10Rebounds = last10Rebounds;
    }

    public void setLast10Assists(double last10Assists) {
        this.last10Assists = last10Assists;
    }

    public void setSeasonPoints(double seasonPoints) {
        this.seasonPoints = seasonPoints;
    }

    public void setSeasonRebounds(double seasonRebounds) {
        this.seasonRebounds = seasonRebounds;
    }

    public void setSeasonAssists(double seasonAssists) {
        this.seasonAssists = seasonAssists;
    }
}
