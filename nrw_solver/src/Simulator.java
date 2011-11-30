package ernst.simulator;

import java.lang.Math;
import java.lang.reflect.Array;
import java.text.DecimalFormat;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;

import ernst.solver.FileLatencyModel;
import ernst.solver.LatencyModel;
import ernst.solver.LatencyModelValidator;

/*
    LEGACY CLASSES, PORTED
 */

class ReadOutput
{
    int version_at_start;
    int version_read;
    double start_time;

    public int getVersion_at_start() {
        return version_at_start;
    }

    public int getVersion_read() {
        return version_read;
    }

    public double getStart_time() {
        return start_time;
    }

    public ReadOutput(int version_at_start, int version_read, double start_time)
    {
        this.version_at_start = version_at_start;
        this.version_read = version_read;
        this.start_time = start_time;
    }
}

class ReadPlot implements Comparable
{
    ReadOutput read;
    double commit_time_at_start;

    public ReadOutput getRead() {
        return read;
    }

    public double getCommit_time_at_start() {
        return commit_time_at_start;
    }

    public ReadPlot(ReadOutput read, double commit_time_at_start)
    {
        this.read = read;
        this.commit_time_at_start = commit_time_at_start;
    }

    public int compareTo(Object anotherPlot) throws ClassCastException
    {
        if(!(anotherPlot instanceof ReadPlot))
            throw new ClassCastException("A ReadPlot object expected.");

        ReadPlot comparePlot = ((ReadPlot) anotherPlot);

        double thisdelta = this.read.getStart_time()-this.commit_time_at_start;
        double theirdelta = comparePlot.getRead().getStart_time()-comparePlot.getCommit_time_at_start();

        if(thisdelta < theirdelta)
            return -1;
        else if(thisdelta == theirdelta)
            return 0;
        else
            return 1;
    }
}

/*
    END LEGACY CLASSES
 */

interface DelayModel
{
    public double getWriteSendDelay();
    public double getReadSendDelay();
    public double getWriteAckDelay();
    public double getReadAckDelay();
}

class ParetoDelayModel implements DelayModel
{
    double wmin, walpha, arsmin, arsalpha;
    Random rand;
    public ParetoDelayModel(double wmin, double walpha, double arsmin, double arsalpha)
    {
        this.wmin = wmin;
        this.walpha = walpha;
        this.arsmin = arsmin;
        this.arsalpha = arsalpha;
        this.rand = new Random();
    }

    double getNextPareto(double m, double a)
    {
        return m / Math.pow(rand.nextDouble(), 1/a);
    }

    public double getWriteSendDelay()
    {
        return getNextPareto(wmin, walpha);
    }

    public double getReadSendDelay()
    {
        return getNextPareto(arsmin, arsalpha);
    }

    public double getWriteAckDelay()
    {
        return getReadSendDelay();
    }

    public double getReadAckDelay()
    {
        return getReadSendDelay();
    }
}


class ExponentialDelayModel implements DelayModel
{
    double wlambda, arslambda;
    Random rand;
    public ExponentialDelayModel(double wlambda, double arslambda)
    {
        this.wlambda = wlambda;
        this.arslambda = arslambda;
        this.rand = new Random();
    }

    double getNextExponential(double lambda)
    {
        return Math.log(1-rand.nextDouble())/(-lambda);
    }

    public double getWriteSendDelay()
    {
        return getNextExponential(wlambda);
    }

    public double getReadSendDelay()
    {
        return getNextExponential(arslambda);
    }

    public double getWriteAckDelay()
    {
        return getReadSendDelay();
    }

    public double getReadAckDelay()
    {
        return getReadSendDelay();
    }
}

class EmpiricalDelayModel implements DelayModel
{
    LatencyModel ackLatencyModel;
    LatencyModel sendLatencyModel;

    Random rand;

    //empirical distribution
    public EmpiricalDelayModel(String sendF, String writeF)
    {
      rand = new Random();

      try{
        sendLatencyModel = new FileLatencyModel(sendF);
        ackLatencyModel = new FileLatencyModel(writeF);
        LatencyModelValidator.ValidateModel(sendLatencyModel);
        LatencyModelValidator.ValidateModel(ackLatencyModel);
       }
       catch (Exception e)
       {
        System.out.println("BAD LATENCY MODEL; EXITING");
        System.out.println(e.getMessage());
        System.exit(-1);
       }
    }

    public double getWriteSendDelay() {
      return sendLatencyModel.getInverseCDF(1,
              rand.nextDouble());
    }

    public double getReadSendDelay() { return getWriteAckDelay(); };

    public double getWriteAckDelay() {
      return ackLatencyModel.getInverseCDF(1,
              rand.nextDouble());
    }

    public double getReadAckDelay() { return getWriteAckDelay(); };
}

class ReadInstance implements Comparable
{
    int version;
    double finishtime;
    int server;

    public int getVersion()
    {
        return version;
    }

    public int getServer()
    {
        return server;
    }

    public double getFinishtime()
    {
        return finishtime;
    }

    public ReadInstance(int version, double finishtime, int sno)
    {
        this.version = version;
        this.finishtime = finishtime;
        this.server = sno;
    }

    public int compareTo(Object anotherRead) throws ClassCastException
    {
        if(!(anotherRead instanceof ReadInstance))
            throw new ClassCastException("A ReadInstance object expected.");

        double otherFinishTime = ((ReadInstance) anotherRead).getFinishtime();

        if(this.finishtime < otherFinishTime)
            return -1;
        else if(this.finishtime == otherFinishTime)
            return 0;
        else
            return 1;
    }}

class WriteInstance implements Comparable
{
    List<Double> oneway;
    double committime;
    double starttime;


    public double getStarttime() {
        return starttime;
    }


    public List<Double> getOneway() {
        return oneway;
    }

    public double getCommittime() {
        return committime;
    }

    public WriteInstance(List<Double> oneway, double starttime, double committime)
    {
        this.oneway = oneway;
        this.starttime = starttime;
        this.committime = committime;
    }

    public int compareTo(Object anotherWrite) throws ClassCastException
    {
        if(!(anotherWrite instanceof WriteInstance))
            throw new ClassCastException("A WriteInstance object expected.");

        double otherStartTime = ((WriteInstance) anotherWrite).getStarttime();

        if(this.starttime < otherStartTime)
            return -1;
        else if(this.starttime == otherStartTime)
            return 0;
        else
            return 1;
    }
}

class CommitTimes
{
    TreeMap<Double, Integer> commits;
    HashMap<Integer, Double> versiontotime;
    HashMap<Double, WriteInstance> timetowrite;

    public CommitTimes()
    {
        commits = new TreeMap<Double, Integer>();
        versiontotime = new HashMap<Integer, Double>();
        timetowrite = new HashMap<Double, WriteInstance>();
    }

    public void record(WriteInstance write, int version)
    {
        commits.put(write.getCommittime(), version);
        versiontotime.put(version, write.getCommittime());
        timetowrite.put(write.getCommittime(), write);
    }

    public WriteInstance get_instance_from_time(double time)
    {
        return timetowrite.get(time);
    }

    public int last_committed_version(double time)
    {
      if(commits.containsKey(time))
          return commits.get(time);
      return commits.get(commits.headMap(time).lastKey());
    }

    public double get_commit_time(int version)
    {
        return versiontotime.get(version);
    }
}

class KVServer {
  TreeMap<Double, Integer> timeVersions;

  public KVServer()
  {
    timeVersions = new TreeMap<Double, Integer>();
  }

  public void write(double time, int version)
  {
    //don't store old versions!
    if(read(time) > version)
    {
        return;
    }

    timeVersions.put(time, version);
  }

  public int read(double time)
  {
    if(timeVersions.containsKey(time))
        return timeVersions.get(time);

    SortedMap<Double, Integer> mapFromTime = timeVersions.headMap(time);
    if(mapFromTime.isEmpty())
        return -1;
    return timeVersions.get(mapFromTime.lastKey());
  }
}

public class Simulator {

  public static void main (String [] args) {
      assert args.length > 5;

      int NUM_READERS = 1;
      int NUM_WRITERS = 1;
      int N = 3, R = 1, W = 1, K = 1, ITERATIONS = 1000, writespacing = 1, readsperwrite = 10;
      DelayModel delaymodel = null;
      boolean multidc = false;
      double dcdelay = 0;


      try
      {
          N = Integer.parseInt(args[0]);
          R = Integer.parseInt(args[1]);
          W = Integer.parseInt(args[2]);
          K = Integer.parseInt(args[3]);
          assert K >= 1;
          ITERATIONS = Integer.parseInt(args[4]);
          writespacing = Integer.parseInt(args[5]);
          readsperwrite = Integer.parseInt(args[6]);

          delaymodel = null;

          if(args[7].equals("FILE"))
          {
              String sendDelayFile = args[8];
              String ackDelayFile = args[9];

              delaymodel = new EmpiricalDelayModel(sendDelayFile, ackDelayFile);
          }
          else if(args[7].equals("PARETO") || args[7].equals("MULTIDC"))
          {
              delaymodel = new ParetoDelayModel(Double.parseDouble(args[8]),
                                           Double.parseDouble(args[9]),
                                           Double.parseDouble(args[10]),
                                           Double.parseDouble(args[11]));

              if(args[7].equals("MULTIDC"))
              {
                  multidc = true;
                  dcdelay = Double.parseDouble(args[12]);
              }
          }
          else if(args[7].equals("EXPONENTIAL"))
          {
              delaymodel = new ExponentialDelayModel(Double.parseDouble(args[8]),
                                                Double.parseDouble(args[9]));
          }
      }
      catch(Exception e)
      {
          e.printStackTrace();
          System.err.println(
             "Usage: Simulator <N> <R> <W> <k> <iters> <write spacing> <readsperwrite> FILE <sendF> <ackF> OPT\n" +
                     "Usage: Simulator <N> <R> <W> <k> <iters> <write spacing> <readsperwrite> PARETO <W-min> <W-alpha> <ARS-min> <ARS-alpha> OPT\n" +
                     "Usage: Simulator <N> <R> <W> <k> <iters> <write spacing> <readsperwrite> EXPONENTIAL <W-lambda> <ARS-lambda> OPT\n" +
                     "Usage: Simulator <N> <R> <W> <k> <iters> <write spacing> <readsperwrite> MULTIDC <W-min> <W-alpha> <ARS-min> <ARS-alpha> <DC-delay> OPT\n" +
                     "OPT= O <SWEEP|LATS|BESTCASE|WORSTCASE>");
          System.exit(1);
      }

      String optsinput = "";

      for(int i = 0; i < args.length; ++i)
      {
          if(args[i].equals("O"))
          {
              optsinput = args[i+1];
              assert optsinput.equals("SWEEP") || optsinput.equals("LATS") || optsinput.equals("BESTCASE")||optsinput.equals("WORSTCASE");
              break;
          }
      }

      final String opts = optsinput;

      final Vector<KVServer> replicas = new Vector<KVServer>();
      for(int i = 0; i < N; ++i)
      {
          replicas.add(new KVServer());
      }

      Vector<Double> writelats = new Vector<Double>();
      final ConcurrentLinkedQueue<Double> readlats = new ConcurrentLinkedQueue<Double>();

      Vector<WriteInstance> writes = new Vector<WriteInstance>();
      final CommitTimes commits = new CommitTimes();

      final ConcurrentLinkedQueue<ReadPlot> readPlotConcurrent = new ConcurrentLinkedQueue<ReadPlot>();

      double ltime = 0;
      double ftime = 1000;

      for(int wid = 0; wid < NUM_WRITERS; wid++)
      {
          double time = 0;
          for(int i = 0; i < ITERATIONS; ++i)
          {
              Vector<Double> oneways = new Vector<Double>();
              Vector<Double> rtts = new Vector<Double>();

              int chosenDC = 0;

              if(multidc)
                  chosenDC = (new Random()).nextInt(N);

              for(int w = 0; w < N; ++w)
              {
                  double onewaydcdelay = 0;
                  double ackdcdelay = 0;

                  if(multidc && w != chosenDC)
                  {
                      onewaydcdelay = dcdelay;
                      ackdcdelay = dcdelay;
                  }

                  double oneway = delaymodel.getWriteSendDelay()+onewaydcdelay;

                  double ack = delaymodel.getWriteAckDelay()+ackdcdelay;
                  oneways.add(time + oneway);
                  rtts.add(oneway + ack);
              }
              Collections.sort(rtts);
              double wlat = rtts.get(W-1);

              if(opts.equals("LATS"))
              {
                  writelats.add(wlat);
              }

              double committime = time+wlat;
              writes.add(new WriteInstance(oneways, time, committime));
              time += writespacing;
          }

          if(time > ltime)
              ltime = time;
          if(time < ftime)
              ftime = time;
      }

      final double maxtime = ltime;
      final double firsttime = ftime;

      Collections.sort(writes);

      for(int wno = 0; wno < writes.size(); ++wno)
      {
          WriteInstance curWrite = writes.get(wno);

          for(int sno = 0; sno < N; ++sno)
          {
              replicas.get(sno).write(curWrite.getOneway().get(sno), wno);
          }
          commits.record(curWrite, wno);
      }

      if(opts.equals("SWEEP") || opts.equals("BESTCASE") || opts.equals("WORSTCASE"))
      {
          HashMap<Double, Long> t_to_current = new HashMap<Double, Long>();
          HashMap<Double, Long> t_to_stale = new HashMap<Double, Long>();
          boolean last_was_one = false;
          for(double ts = 0; ts < 300; ts++)
          {
              long current = 0;
              long stale = 0;
              for(WriteInstance write : writes)
              {
                  double time = write.getCommittime()+ts;
                  if(time > maxtime)
                      continue;

                  for(int r = 0; r < readsperwrite; r++)
                  {
                      Vector<ReadInstance> readRound = new Vector<ReadInstance>();

                      int thisdc = (new Random()).nextInt(N);

                      for(int sno = 0; sno < N; ++sno)
                      {
                          double onewaydcdelay = 0;
                          double ackdcdelay = 0;

                          if(multidc && (sno != thisdc))
                          {
                              onewaydcdelay = dcdelay;
                              ackdcdelay = dcdelay;
                          }

                          double onewaytime = onewaydcdelay+delaymodel.getReadSendDelay();
                          int version = replicas.get(sno).read(time+onewaytime);
                          double rtt = onewaytime+ackdcdelay+delaymodel.getReadAckDelay();

                          readRound.add(new ReadInstance(version, rtt, sno));
                      }

                      Vector<ReadInstance> readRoundSort = (Vector<ReadInstance>)readRound.clone();
                      Collections.sort(readRoundSort);
                      double endtime = readRoundSort.get(R-1).getFinishtime();

                      if(opts.equals("BESTCASE") || opts.equals("WORSTCASE"))
                      {
                          WriteInstance w = commits.get_instance_from_time(commits.get_commit_time(commits.last_committed_version(time)));
                          List<Double> oneway_writes = w.getOneway();

                          Map<Double, Integer> map = new TreeMap<Double, Integer>();
                          for(int i = 0; i < oneway_writes.size(); ++i)
                          {
                              map.put(oneway_writes.get(i), i);
                          }

                          Vector<ReadInstance> filteredReadRound = new Vector<ReadInstance>();
                          List<Integer> index_to_order = new Vector<Integer>(map.values());

                          if(opts.equals("BESTCASE"))
                          {
                             for(int i = 0; i < R; ++i)
                             {
                                 filteredReadRound.add(readRound.get(index_to_order.get(i)));
                             }
                          }
                          else if(opts.equals("WORSTCASE"))
                          {
                             for(int i = N-R; i < N; ++i)
                             {
                                 filteredReadRound.add(readRound.get(index_to_order.get(i)));
                             }
                          }

                          readRound = filteredReadRound;
                      }

                      Collections.sort(readRound);

                      int maxversion = -1;

                      for(int rno = 0; rno < R; ++rno)
                      {
                        int readVersion = readRound.get(rno).getVersion();
                        if(readVersion > maxversion)
                            maxversion = readVersion;
                      }

                      double t = time-commits.get_commit_time(commits.last_committed_version(time));

                      t = Math.round(t*10)/10.0d;

                      if(maxversion < commits.last_committed_version(time)-(K-1))
                      {
                          if(!t_to_stale.containsKey(t))
                          {
                              t_to_stale.put(t, 0l);
                          }

                          t_to_stale.put(t, t_to_stale.get(t)+1);
                      }
                      else
                      {
                          if(!t_to_current.containsKey(t))
                          {
                              t_to_current.put(t, 0l);
                          }

                          t_to_current.put(t, t_to_current.get(t)+1);
                      }
                  }
              }
          }


          List<Double> times = new Vector<Double>(t_to_stale.keySet());

          List<Double> curtimes = new Vector<Double>(t_to_current.keySet());
          Collections.sort(curtimes);

          //Le sigh; I miss list comprehensions

          long toadd = 3;
          for(double curtime : curtimes)
          {
              /*
                Add the first time at which we don't have any stale readings;
                Only add the first few given that as time goes on, we shouldn't observe
                more staleness (except for a bit of noise due to experimental error).
               */
              if(!t_to_stale.containsKey(curtime))
              {
                  times.add(curtime);
                  toadd--;
                  if(toadd == 0)
                  break;
              }
          }

          Collections.sort(times);

          if(times.isEmpty())
              System.out.println("0.0 1.0");

          for(double ts : times)
          {
              long stales = t_to_stale.containsKey(ts) ? t_to_stale.get(ts) : 0;
              long current = t_to_current.containsKey(ts) ? t_to_current.get(ts) : 0;
              System.out.println((float)(current)/(current+stales)+" "+ts);
          }
      }

      if(opts.equals("LATS"))
      {
          System.out.println("WRITE");
          Collections.sort(writelats);
          for(double p = 0; p < 1; p += .01)
          {
              int index = (int)Math.round(p*writelats.size());
              if(index >= writelats.size())
                  break;
              System.out.printf("%f %f\n", p, writelats.get(index));
          }

          double lastp = .99;
          for(int i = 3; i < 7; ++i)
          {
              lastp += 9*Math.pow(10, -i);
              int index = (int)Math.round(lastp*writelats.size());
              if(index >= writelats.size())
                  break;
              System.out.printf("%f %f\n", lastp, writelats.get(index));
          }

          Vector<Double> readLatencies = new Vector<Double>();

          for(int i = 0; i < ITERATIONS; ++i)
          {
              Vector<Double> thisreadround = new Vector<Double>();

              int thisdc = (new Random()).nextInt(N);

              for(int sno = 0; sno < N; ++sno)
              {
                  double onewaydcdelay = 0;
                  double ackdcdelay = 0;

                  if(multidc && (sno != thisdc))
                  {
                      onewaydcdelay = dcdelay;
                      ackdcdelay = dcdelay;
                  }

                  double onewaytime = onewaydcdelay+delaymodel.getReadSendDelay();
                  double rtt = onewaytime+ackdcdelay+delaymodel.getReadAckDelay();
                  thisreadround.add(rtt);
              }

              Collections.sort(thisreadround);
              double endtime = thisreadround.get(R-1);
              readLatencies.add(endtime);
          }

          System.out.println("READ");
          Collections.sort(readLatencies);
          for(double p = 0; p < 1; p += .01)
          {
              int index = (int)Math.round(p*readLatencies.size());
              if(index >= readLatencies.size())
                  break;
              System.out.printf("%f %f\n", p, readLatencies.get(index));
          }

          lastp = .99;
          for(int i = 3; i < 7; ++i)
          {
              lastp += 9*Math.pow(10, -i);
              int index = (int)Math.round(lastp*readLatencies.size());
              if(index >= readLatencies.size())
                  break;
              System.out.printf("%f %f\n", lastp, readLatencies.get((int) Math.round(lastp * readLatencies.size())));
          }

      }
  }
}
