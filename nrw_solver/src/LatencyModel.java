package ernst.solver;

import java.util.List;

public interface LatencyModel {
    //t in seconds
    public double getLatencyPDF(int numReplicas, double t);
    public double getLatencyCDF(int numReplicas, double t);
    public List<Double> getRange(int numReplicas);
}
