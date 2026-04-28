/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package predictions;

/**
 *
 * @author 1zomb
 */
public class Prediction {
    private String playerName;
    private String opponent;
    private String team_abbreviation;
    private double predPoints;
    private double predRebounds;
    private double predAssists;
    private double predPRA;
    private double last5Points;
    private double last5Rebounds;
    private double last5Assists;

    public Prediction(String playerName, String opponent,String team_abbreviation, double predPoints,
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

    public String getPlayerName() {
        return playerName;
    }

    public String getOpponent() {
        return opponent;
    }
    
    public String getTeam(){
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

    public double getLast5Points() {
        return last5Points;
    }

    public double getLast5Rebounds() {
        return last5Rebounds;
    }

    public double getLast5Assists() {
        return last5Assists;
    }
    
    

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

    public void setLast5Points(double last5Points) {
        this.last5Points = last5Points;
    }

    public void setLast5Rebounds(double last5Rebounds) {
        this.last5Rebounds = last5Rebounds;
    }

    public void setLast5Assists(double last5Assists) {
        this.last5Assists = last5Assists;
    }
    
}
