import java.util.List;

public interface LatencyModel {
    //t in seconds
    public double getLatencyPDF(double t);
    public double getLatencyCDF(double t);
    public List<Double> getRange();
}
