package predictions;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/nba_dfs_dashboard")
public class ProjectionServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        PredictionsDAO dao = new PredictionsDAO();

        ArrayList<Prediction> allPredictions;
        HashMap<String, String> gameMap = new HashMap<>();
        String[][] slate;

        // Hard code slate
        slate = new String[][]{
            {"SAS", "NYK"}
        };

        // Fetch predictions for the slate
        allPredictions = dao.getPredictionsForSlate(slate);
        int gamesOnSlateCount = slate.length;

        // Build dropdown lists
        ArrayList<String> activeMatchups = new ArrayList<>();
        ArrayList<String> activeTeams = new ArrayList<>();

        for (String[] game : slate) {
            String away = game[0];
            String home = game[1];

            String officialMatchup = away + " @ " + home;
            gameMap.put(away, officialMatchup);
            gameMap.put(home, officialMatchup);

            // Grab the specific games and teams for the dropdowns
            activeMatchups.add(officialMatchup);
            activeTeams.add(away);
            activeTeams.add(home);
        }

        // Sort them alphabetically
        Collections.sort(activeMatchups);
        Collections.sort(activeTeams);

        // Set attributes and forward to JSP
        request.setAttribute("predictions", allPredictions);
        request.setAttribute("totalSlatePlayers", allPredictions.size());
        request.setAttribute("gamesOnSlate", gamesOnSlateCount);
        request.setAttribute("teams", activeTeams);
        request.setAttribute("matchups", activeMatchups);
        request.setAttribute("gameMap", gameMap);

        request.getRequestDispatcher("nba_dfs_dashboard.jsp").forward(request, response);
    }
}
