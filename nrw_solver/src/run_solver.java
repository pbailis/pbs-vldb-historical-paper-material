
import java.io.FileReader;
import java.util.Iterator;
import java.util.List;

import java.io.IOException;
import java.util.Properties;

public class run_solver {

    public static void main(String [ ] args) throws IOException
    {
        String propertiesFile = "solver.properties";

        if (args.length == 1)
        {
            propertiesFile = args[0];
        }
        else
        {
          System.out.printf("no solver file specified, using default (%s)\n", propertiesFile);
        }

        Properties configFile = new Properties();
        configFile.load(new FileReader(propertiesFile));

        //number of replicas
        int n = Integer.parseInt(configFile.get("n").toString());
        //minimum number of writes to commit (keep w_min < n)
        int w_min = Integer.parseInt(configFile.get("wmin").toString());

        //maximum probability of staler-than-promised-ness
        double p_s = Double.parseDouble(configFile.get("p_s").toString());

        //RT-staleness, in seconds
        double t = Double.parseDouble(configFile.get("t-stale").toString());
        //k-staleness
        int k = Integer.parseInt(configFile.get("k-stale").toString());

        //relative weighting of read latency
        double c_r = Double.parseDouble(configFile.get("c_r").toString());
        //relative weighting of write latency
        double c_w = Double.parseDouble(configFile.get("c_w").toString());

        /*
        We require three single-replica latency models (IID, remember!):
            a model for read operation completion,
            a model for write operation completion,
            and a model for how fast writes get to a replica
            (the last is called wmodelnoack).
         */

        LatencyModel rmodel = new FileLatencyModel((String)configFile.get("r-latency-model"));
        LatencyModel wmodel = new FileLatencyModel((String)configFile.get("w-latency-model"));
        LatencyModel ackmodel = new FileLatencyModel((String)configFile.get("ack-latency-model"));

        try{
            LatencyModelValidator.ValidateModel(rmodel);
            LatencyModelValidator.ValidateModel(wmodel);
            LatencyModelValidator.ValidateModel(ackmodel);
        }
        catch (Exception e)
        {
            System.out.println("BAD LATENCY MODEL; EXITING");
            System.out.println(e.getMessage());
            System.exit(-1);
        }


        nrw_solver solver = new nrw_solver(p_s, t, k, c_r, c_w, rmodel, wmodel, ackmodel, w_min, n);

        List<nrw_solution> results = solver.get_solutions();
        Iterator<nrw_solution> it = results.iterator();


        while(it.hasNext())
        {
            nrw_solution cur = it.next();

            System.out.printf("\nN: %d\nR: %d\nW: %d\np_s: %f\nFIT: %f\nr_L: %f\nw_L: %f\n", cur.getN(), cur.getR(),
                                cur.getW(), cur.getP_s(), cur.getFitness(), cur.getReadLatency(), cur.getWriteLatency());
        }
    }
}
