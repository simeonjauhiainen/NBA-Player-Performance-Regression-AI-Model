/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package predictions;

import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author 1zomb
 */
public class MergeSort {
       public List<Prediction> mergeSort(List<Prediction> predictions, String stat){
       
       if (predictions.size() <= 1){
           return predictions;
       }
       
       int midpoint = predictions.size() / 2;
       
       
       // Wrapping the sublist with a new arraylist to protect the original list from any modifications
       List<Prediction> left = new ArrayList<>(predictions.subList(0,midpoint));
       List<Prediction> right = new ArrayList<>(predictions.subList(midpoint, predictions.size()));
       
       List<Prediction> sortedLeft = mergeSort(left,stat);
       List<Prediction> sortedRight = mergeSort(right,stat);
      
       
       
       return mergeHalves(sortedLeft, sortedRight,stat);
       
       
}
       
       private double getStatValue(Prediction prediction, String stat) {
    stat = stat.toLowerCase();

    if (stat.equals("points")) {
        return prediction.getPredPoints();
    } else if (stat.equals("rebounds")) {
        return prediction.getPredRebounds();
    } else if (stat.equals("assists")) {
        return prediction.getPredAssists();
    } else if (stat.equals("pra")) {
        return prediction.getPredPRA();
    } else {
        throw new IllegalArgumentException("Unknown stat: " + stat);
    }
}
       
       private List<Prediction> mergeHalves( List<Prediction> sortedLeft,  List<Prediction> sortedRight, String stat) {
    List<Prediction> sortedResults = new ArrayList<>();

    int i = 0;
    int j = 0;

    while (i < sortedLeft.size() && j < sortedRight.size()) {

        double leftStats = getStatValue(sortedLeft.get(i), stat);
        double rightStats = getStatValue(sortedRight.get(j), stat);

        // Descending order: highest stat first
        if (leftStats >= rightStats) {
            sortedResults.add(sortedLeft.get(i));
            i++;
        } else {
            sortedResults.add(sortedRight.get(j));
            j++;
        }
    }

    // Add leftovers from left side
    while (i < sortedLeft.size()) {
        sortedResults.add(sortedLeft.get(i));
        i++;
    }

    // Add leftovers from right side
    while (j < sortedRight.size()) {
        sortedResults.add(sortedRight.get(j));
        j++;
    }

    return sortedResults;
}

}
