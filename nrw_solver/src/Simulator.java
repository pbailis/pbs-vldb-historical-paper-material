package ernst.simulator;

import java.lang.Math;
import java.util.*;

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
    long start_time;

    public int getVersion_at_start() {
        return version_at_start;
    }

    public int getVersion_read() {
        return version_read;
    }

    public long getStart_time() {
        return start_time;
    }

    public ReadOutput(int version_at_start, int version_read, long start_time)
    {
        this.version_at_start = version_at_start;
        this.version_read = version_read;
        this.start_time = start_time;
    }
}

class ReadPlot implements Comparable
{
    ReadOutput read;
    long commit_time_at_start;

    public ReadOutput getRead() {
        return read;
    }

    public long getCommit_time_at_start() {
        return commit_time_at_start;
    }

    public ReadPlot(ReadOutput read, long commit_time_at_start)
    {
        this.read = read;
        this.commit_time_at_start = commit_time_at_start;
    }

    public int compareTo(Object anotherPlot) throws ClassCastException
    {
        if(!(anotherPlot instanceof ReadPlot))
            throw new ClassCastException("A ReadPlot object expected.");

        ReadPlot comparePlot = ((ReadPlot) anotherPlot);

        long thisdelta = this.read.getStart_time()-this.commit_time_at_start;
        long theirdelta = comparePlot.getRead().getStart_time()-comparePlot.getCommit_time_at_start();

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

class DelayModel
{
    LatencyModel ackLatencyModel;
    LatencyModel sendLatencyModel;
    double LAMBDA;
    Random rand;
    int MAX_DELAY = 1000;

    public DelayModel(String sendF, String writeF)
    {
      rand = new Random();
      LAMBDA = 0.05;


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

    public long getExpRandom() {
      return Math.round(Math.log(1-rand.nextDouble())/(-LAMBDA));
    }

    public long getUniformRandom() {
      return rand.nextInt(MAX_DELAY);
    }

    public long getWriteSendDelay() {
      return Math.round(sendLatencyModel.getInverseCDF(1,
          rand.nextDouble()));
    }

    public long getReadSendDelay() { return getWriteSendDelay(); };

    public long getWriteAckDelay() {
      return Math.round(ackLatencyModel.getInverseCDF(1,
          rand.nextDouble()));
    }

    public long getReadAckDelay() { return getWriteAckDelay(); };
}

class ReadInstance implements Comparable
{
    int version;
    long finishtime;

    public int getVersion() {
        return version;
    }

    public long getFinishtime() {
        return finishtime;
    }

    public ReadInstance(int version, long finishtime)
    {
        this.version = version;
        this.finishtime = finishtime;
    }

    public int compareTo(Object anotherRead) throws ClassCastException
    {
        if(!(anotherRead instanceof ReadInstance))
            throw new ClassCastException("A ReadInstance object expected.");

        long otherFinishTime = ((ReadInstance) anotherRead).getFinishtime();

        if(this.finishtime < otherFinishTime)
            return -1;
        else if(this.finishtime == otherFinishTime)
            return 0;
        else
            return 1;
    }}

class WriteInstance implements Comparable
{
    List<Long> oneway;
    long committime;
    long starttime;


    public long getStarttime() {
        return starttime;
    }


    public List<Long> getOneway() {
        return oneway;
    }

    public long getCommittime() {
        return committime;
    }

    public WriteInstance(List<Long> oneway, long starttime, long committime)
    {
        this.oneway = oneway;
        this.starttime = starttime;
        this.committime = committime;
    }

    public int compareTo(Object anotherWrite) throws ClassCastException
    {
        if(!(anotherWrite instanceof WriteInstance))
            throw new ClassCastException("A WriteInstance object expected.");

        long otherStartTime = ((WriteInstance) anotherWrite).getStarttime();

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
    TreeMap<Long, Integer> commits;
    HashMap<Integer, Long> versiontotime;

    public CommitTimes()
    {
        commits = new TreeMap<Long, Integer>();
        versiontotime = new HashMap<Integer, Long>();
    }

    public void record(long time, int version)
    {
      commits.put(time, version);
      versiontotime.put(version, time);
    }

    public int last_committed_version(long time)
    {
      if(commits.containsKey(time))
          return commits.get(time);
      return commits.get(commits.headMap(time).firstKey());
    }

    public long get_commit_time(int version)
    {
        return versiontotime.get(version);
    }
}

class KVServer {
  TreeMap<Long, Integer> timeVersions;

  public KVServer()
  {
    timeVersions = new TreeMap<Long, Integer>();
  }

  public void write(long time, int version)
  {
    timeVersions.put(time, version);
  }

  public int read(long time)
  {
    if(timeVersions.containsKey(time))
        return timeVersions.get(time);
    return timeVersions.get(timeVersions.headMap(time).firstKey());
  }
}

public class Simulator {
  public static void main (String [] args) {
      if(args.length != 6)
      {
        System.err.println(
          "Usage: Simulator <N> <R> <W> <iters> <sendF> <ackF>");
        System.exit(1);
      }

      int NUM_READERS = 5;
      int NUM_WRITERS = 1;

      int N = Integer.parseInt(args[0]);
      int R = Integer.parseInt(args[1]);
      int W = Integer.parseInt(args[2]);
      int ITERATIONS = Integer.parseInt(args[3]);
      String sendDelayFile = args[4];
      String ackDelayFile = args[5];

      DelayModel delay = new DelayModel(sendDelayFile, ackDelayFile);

      Vector<KVServer> replicas = new Vector<KVServer>();
      for(int i = 0; i < N; ++i)
      {
          replicas.add(new KVServer());
      }


      HashMap<Integer, Long> commitTimes = new HashMap<Integer, Long>();
      Vector<WriteInstance> writes = new Vector<WriteInstance>();
      CommitTimes commits = new CommitTimes();

      Vector<ReadPlot> readPlots = new Vector<ReadPlot>();

      long maxtime = 0;
      long firsttime = 1000;

      for(int wid = 0; wid < NUM_WRITERS; wid++)
      {
          long time = 0;
          for(int i = 0; i < ITERATIONS; ++i)
          {
              Vector<Long> oneways = new Vector<Long>();
              Vector<Long> rtts = new Vector<Long>();
              for(int w = 0; w < N; ++w)
              {
                  long oneway = delay.getWriteSendDelay();
                  long ack = delay.getWriteAckDelay();
                  oneways.add(time+oneway);
                  rtts.add(oneway+ack);
              }
              Collections.sort(rtts);
              long committime = time+rtts.get(W-1);
              writes.add(new WriteInstance(oneways, time, committime));
              time = committime;
          }

          if(time > maxtime)
              maxtime = time;
          if(time < firsttime)
              firsttime = time;
      }

      Collections.sort(writes);

      for(int wno = 0; wno < writes.size(); ++wno)
      {
          WriteInstance curWrite = writes.get(wno);
          for(int sno = 0; sno < N; ++sno)
          {
              replicas.get(sno).write(curWrite.getOneway().get(sno), wno);
          }
          commits.record(curWrite.getCommittime(), wno);
      }

      for(int rid = 0; rid < NUM_READERS; ++rid)
      {
          long time = firsttime*2;
          while(time < maxtime)
          {
              Vector<ReadInstance> readRound = new Vector<ReadInstance>();
              for(int sno = 0; sno < N; ++sno)
              {
                  long onewaytime = delay.getReadSendDelay();
                  int version = replicas.get(sno).read(time+onewaytime);
                  long rtt = onewaytime+delay.getReadAckDelay();
                  readRound.add(new ReadInstance(version, rtt));
              }

              Collections.sort(readRound);
              long endtime = readRound.get(R-1).getFinishtime();

              int maxversion = -1;

              for(int rno = 0; rno < R; ++rno)
              {
                int readVersion = readRound.get(rno).getVersion();
                if(readVersion > maxversion)
                    maxversion = readVersion;
              }

              readPlots.add(new ReadPlot(
                                new ReadOutput(commits.last_committed_version(time), maxversion, time),
                                commits.get_commit_time(maxversion)));
              int staleness = maxversion-commits.last_committed_version(time);

              time += endtime;
          }
      }

      Collections.sort(readPlots);
      Collections.reverse(readPlots);

      for(int p = 900; p < 1000; ++p)
      {
          long tstale = 0;
          int staler = 0;
          int current = 0;
          boolean tstaleComputed = false;
          Double pst = (1-p)/1000.0;

          long how_many_stale = (long)Math.ceil(readPlots.size()*pst);

          for(ReadPlot r : readPlots)
          {
            if(r.getRead().getVersion_read() >= r.getRead().getVersion_at_start())
            {
                current += 1;
            }
            else
            {
                staler += 1;
            }

            if((staler > how_many_stale) && !tstaleComputed)
            {
                tstaleComputed = true;
                tstale = r.getRead().getStart_time() - r.getCommit_time_at_start();
            }
          }
          System.out.println(p+" "+tstale);
      }
  }
}
