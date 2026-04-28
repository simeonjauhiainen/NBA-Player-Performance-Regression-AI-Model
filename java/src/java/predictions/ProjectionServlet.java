/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package predictions;

/**
 *
 * @author 1zomb
 */
import java.io.IOException;
import java.util.ArrayList;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/nba_dfs_dashboard")
public class ProjectionServlet extends HttpServlet{
 
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        PredictionsDAO dao = new PredictionsDAO();
        String date = request.getParameter("date");
        String[][] slate;

        if ("2026-04-28".equals(date)) {
     slate = new String[][] {
        {"BOS", "PHI"},
        {"POR", "SAS"},
        {"ATL", "NYK"}
    };
} 
else if ("2026-04-29".equals(date)) {
    slate = new String[][] {
        {"DET", "ORL"},
        {"CLE", "TOR"},
        {"OKC", "PHX"},
        {"LAL", "HOU"} 
    };
    }
    else {
    slate = new String[][] {
        {"ORL", "DET"},
        {"PHX", "OKC"},
        {"DEN","MIN"}
    };
}

        ArrayList<Prediction> allPredictions = dao.getPredictionsForSlate(slate);

        int totalSlatePlayers = allPredictions.size();

        ArrayList<Prediction> top5;

        if (allPredictions.size() > 5) {
            top5 = new ArrayList<>(allPredictions.subList(0, 5));
        } else {
            top5 = allPredictions;
        }

       request.setAttribute("predictions", allPredictions);
       request.setAttribute("topN", 5);
       request.setAttribute("totalSlatePlayers", totalSlatePlayers);
       request.setAttribute("gamesOnSlate", slate.length);
  
       ArrayList<String> teams = new ArrayList<>();
ArrayList<String> matchups = new ArrayList<>();

for (String[] game : slate) {
    String t1 = game[0];
    String t2 = game[1];

    teams.add(t1);
    teams.add(t2);

    matchups.add(t1 + " @ " + t2);
    matchups.add(t2 + " @ " + t1);
}

request.setAttribute("teams", teams);
request.setAttribute("matchups", matchups);

        request.getRequestDispatcher("nba_dfs_dashboard.jsp")
               .forward(request, response);
}
}
