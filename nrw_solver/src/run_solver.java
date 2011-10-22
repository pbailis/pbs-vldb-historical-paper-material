import sun.java2d.pipe.SpanShapeRenderer;

import java.util.Iterator;
import java.util.List;

public class run_solver {

    public static void main(String [ ] args)
    {
        double p_s = 0;
        double t = 0;
        double c_r = .5;
        double c_w = .5;
        int k = 1;
        int n = 10;
        int w_min = 1;

        LatencyModel rmodel, wmodel, wmodelnoack = new SimpleLatencyModel();

        rmodel = wmodelnoack;
        wmodel = wmodelnoack;


        try{
            LatencyModelValidator.ValidateModel(wmodel);
        }
        catch (Exception e)
        {
            System.out.println("BAD LATENCY MODEL; EXITING");
            System.out.println(e.getMessage());
            System.exit(-1);
        }


        nrw_solver solver = new nrw_solver(p_s, t, k, c_r, c_w, rmodel, wmodel, wmodelnoack, w_min, n);

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
