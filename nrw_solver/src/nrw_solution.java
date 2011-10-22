
public class nrw_solution {

    private int r;
    private int w;
    private double fitness;
    private int n;
    private double p_s;
    private double readlatency;
    private double writelatency;


    public nrw_solution(int n, int r, int w, double readlatency, double writelatency, double fitness, double p_s)
    {
        this.n = n;
        this.r = r;
        this.w = w;
        this.readlatency = readlatency;
        this.writelatency = writelatency;
        this.fitness = fitness;
        this.p_s = p_s;
    }

    public int getN() {
        return n;
    }

    public int getR() {
        return r;
    }

    public int getW() {
        return w;
    }

    public double getP_s() {
        return p_s;
    }

    public double getReadLatency()
    {
        return readlatency;
    }

    public double getWriteLatency()
    {
        return writelatency;
    }

    public double getFitness() {
        return fitness;
    }
}
