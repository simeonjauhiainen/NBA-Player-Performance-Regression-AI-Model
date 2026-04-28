<%@ page import="java.util.ArrayList" %>
<%@ page import="predictions.Prediction" %>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NBA DFS Projection Dashboard</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: Arial, Helvetica, sans-serif;
    }

    body {
      background: #f4f7fb;
      color: #1f2937;
    }

    .container {
      width: 90%;
      max-width: 1200px;
      margin: 0 auto;
      padding: 30px 0 50px;
    }

    .header {
      background: linear-gradient(135deg, #0f172a, #1d4ed8);
      color: white;
      padding: 28px;
      border-radius: 16px;
      margin-bottom: 24px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }

    .header h1 {
      font-size: 2rem;
      margin-bottom: 8px;
    }

    .header p {
      font-size: 1rem;
      color: #dbeafe;
    }

    .filters {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .filter-box {
      background: white;
      padding: 16px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    .filter-box label {
      display: block;
      font-size: 0.9rem;
      font-weight: bold;
      margin-bottom: 8px;
      color: #374151;
    }

    .filter-box input,
    .filter-box select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 0.95rem;
    }

    .summary-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .card {
      background: white;
      padding: 20px;
      border-radius: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
      border-left: 5px solid #2563eb;
    }

    .card h3 {
      font-size: 0.95rem;
      color: #6b7280;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .card .value {
      font-size: 1.6rem;
      font-weight: bold;
      color: #111827;
    }

    .table-section {
      background: white;
      border-radius: 16px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.07);
      overflow: hidden;
    }

    .table-header {
      padding: 18px 20px;
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }

    .table-header h2 {
      font-size: 1.2rem;
    }

    .table-wrapper {
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 900px;
    }

    th, td {
      padding: 14px 16px;
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
      font-size: 0.95rem;
    }

    th {
      background: #eff6ff;
      color: #1e3a8a;
      font-weight: 700;
    }

    tr:hover {
      background: #f9fafb;
    }

    .player-name {
      font-weight: bold;
      color: #111827;
    }

    .highlight {
      font-weight: bold;
      color: #1d4ed8;
    }

    .footer-note {
      margin-top: 18px;
      font-size: 0.9rem;
      color: #6b7280;
    }

    @media (max-width: 768px) {
      .header h1 {
        font-size: 1.6rem;
      }

      .card .value {
        font-size: 1.3rem;
      }
    }
  </style>
</head>
<body>
  <div class="container">
   <%
    ArrayList<Prediction> predictions =
        (ArrayList<Prediction>) request.getAttribute("predictions");

    Integer totalSlatePlayers =
        (Integer) request.getAttribute("totalSlatePlayers");

    Integer gamesOnSlate =
        (Integer) request.getAttribute("gamesOnSlate");

    Prediction topPlayer = null;
    double highestPra = 0.0;
    int totalPlayers = totalSlatePlayers != null ? totalSlatePlayers : 0;
    int totalGames = gamesOnSlate != null ? gamesOnSlate : 0;

    if (predictions != null && !predictions.isEmpty()) {
        topPlayer = predictions.get(0);
        highestPra = topPlayer.getPredPRA();
    }
%>
    <section class="header">
      <h1>NBA DFS Projection Dashboard</h1>
      <p>Projected player points, rebounds, assists, and PRA for todays slate.</p>
    </section>

    <section class="filters">
      <div class="filter-box">
        <label for="search">Search Player</label>
        <input type="text" id="search" placeholder="Search by player name" />
      </div>

      <div class="filter-box">
        <label for="team">Team</label>
        <select id="team">
    <option>All Teams</option>
    <%
        ArrayList<String> teams = (ArrayList<String>) request.getAttribute("teams");
        for (String t : teams) {
    %>
        <option><%= t %></option>
    <%
        }
    %>
</select>
      </div>

      <div class="filter-box">
        <label for="matchup">Matchup</label>
       <select id="matchup">
    <option>All Matchups</option>
    <%
        ArrayList<String> matchups = (ArrayList<String>) request.getAttribute("matchups");
        for (String m : matchups) {
    %>
        <option><%= m %></option>
    <%
        }
    %>
</select>
      </div>

      <div class="filter-box">
        <label for="date">Slate Date</label>
      <form method="get" action="nba_dfs_dashboard">
        <input type="date" id="date" name="date" onchange="this.form.submit()" />
     </form>
      </div>
    </section>

    <section class="summary-cards">
      <div class="card">
        <h3>Top Projected Player</h3>
     <div class="value"><%= topPlayer != null ? topPlayer.getPlayerName() : "N/A" %></div>
      </div>

      <div class="card">
        <h3>Highest PRA</h3>
        <div class="value"><%= highestPra %></div>
      </div>

      <div class="card">
        <h3>Games on Slate</h3>
      <div class="value"><%= totalGames %></div>
      </div>

      <div class="card">
        <h3>Total Players</h3>
       <div class="value"><%= totalPlayers %></div>
      </div>
    </section>

    <section class="table-section">
      <div class="table-header">
        <h2>Projected Player Stats</h2>
        <span>Last updated: <%= new java.util.Date() %></span>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Player</th>
              <th>Team</th>
              <th>Matchup</th>
              <th>Proj PTS</th>
              <th>Proj REB</th>
              <th>Proj AST</th>
              <th>Proj PRA</th>
              <th>Last 5 PTS</th>
              <th>Last 5 REB</th>
              <th>Last 5 AST</th>
            </tr>
          </thead>
          <tbody>
        <%
  if (predictions != null && !predictions.isEmpty()) {

    int count = 0;
    int topN = request.getAttribute("topN") != null ? (Integer) request.getAttribute("topN") : 5;

    for (Prediction p : predictions) {
        boolean show = count < topN;
        count++;
%>
<tr class="player-row" style="<%= show ? "" : "display:none;" %>">
    <td class="player-name"><%= p.getPlayerName() %></td>
    <td><%= p.getTeam() %></td>
   <td><%= p.getTeam() %> @ <%= p.getOpponent() %></td>
    <td><%= p.getPredPoints() %></td>
    <td><%= p.getPredRebounds() %></td>
    <td><%= p.getPredAssists() %></td>
    <td class="highlight"><%= p.getPredPRA() %></td>
    <td><%= p.getLast5Points() %></td>
    <td><%= p.getLast5Rebounds() %></td>
    <td><%= p.getLast5Assists() %></td>
</tr>
<%
        }
    } else {
%>
<tr>
    <td colspan="10">No predictions found.</td>
</tr>
<%
    }
%>
          </tbody>
        </table>
      </div>
    </section>

    <p class="footer-note">
    </p>
  </div>
   
<script>
 document.addEventListener("DOMContentLoaded", function () {

    console.log("script loaded");

    document.getElementById("search").addEventListener("input", filterTable);
    document.getElementById("team").addEventListener("change", filterTable);
    document.getElementById("matchup").addEventListener("change", filterTable);

    function filterTable() {
        const search = document.getElementById("search").value.toLowerCase();
        const team = document.getElementById("team").value;
        const matchup = document.getElementById("matchup").value;

        const rows = document.querySelectorAll(".player-row");

        rows.forEach(row => {
            const player = row.cells[0].innerText.toLowerCase();
            const rowTeam = row.cells[1].innerText;
            const rowMatchup = row.cells[2].innerText;

            let show = true;

            if (search && !player.includes(search)) show = false;
            if (team !== "All Teams" && rowTeam !== team) show = false;
            if (matchup !== "All Matchups" && rowMatchup !== matchup) show = false;

            row.style.display = show ? "" : "none";
        });
    }

});
</script>       
</body>
</html>
