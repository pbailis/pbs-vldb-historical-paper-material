package ernst.solver;

import java.util.Iterator;
import java.util.List;


//TODO replace with exceptions
public class LatencyModelValidator {
    private static int NUM_REPLICAS = 1;
    static boolean ValidateModel(LatencyModel toCheck) throws RuntimeException
    {
        List<Double> domain = toCheck.getRange(NUM_REPLICAS);

        //check that sum over domain is 1.0
        double accum = 0;
        for(Iterator<Double> it = domain.iterator(); it.hasNext();)
        {
            accum += toCheck.getLatencyPDF(NUM_REPLICAS, it.next());
        }

        if(Math.round(accum*10000.0) != 10000.0)
            throw new RuntimeException(String.format("PDF did not sum to 1.0; summed to %f", accum));

        double prev = 0.0, cur;
        //check that CDF is monotonically increasing
        for(Iterator<Double> it = domain.iterator(); it.hasNext();)
        {
            cur = toCheck.getLatencyCDF(NUM_REPLICAS, it.next());
            if(cur < prev)
            {
                throw new RuntimeException(String.format("CDF is not monotonically increasing; %f > %f", prev, cur));
            }

            prev = cur;
        }

        if(Math.round(prev*10000.0) != 10000.0)
        {
            throw new RuntimeException(String.format("CDF does not go to 1.0; goes to %f", prev));
        }

        return true;
    }
}
