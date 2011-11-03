import java.util.List;
import java.util.Vector;

public class SimpleLatencyModel implements LatencyModel {
    private List<Double> range;

    public SimpleLatencyModel()
    {
        range = new Vector<Double>();

        for(int i = 1; i <= 1000; ++i)
        {
            range.add((double)i/1000.0);
        }
    }


    public double getLatencyPDF(int numReplicas, double t)
    {
        if(t==0)
            return 0;

        if(t <= 1.0 && (double)(int) (t*1000.0) == t*1000.0)
        {
            return .001;
        }

        return 0.0;
    }

    public double getLatencyCDF(int numReplicas, double t)
    {
        if(t==0)
            return 0;
        return Math.min(1.0, Math.floor((t+.001)*1000.0)/1000.0);
    }

    public List<Double> getRange(int numReplicas)
    {
        return range;
    }
}
