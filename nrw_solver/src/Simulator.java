package ernst.simulator;

import java.lang.Math;
import java.util.*;

import ernst.solver.FileLatencyModel;
import ernst.solver.LatencyModel;
import ernst.solver.LatencyModelValidator;
import sun.reflect.generics.tree.Tree;


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

class CommitTimes {
    TreeMap<Long, Integer> commits;

    public CommitTimes()
    {
        commits = new TreeMap<Long, Integer>();
    }

    public void record(long time, int version)
    {
      commits.put(time, version);
    }

    public int last_committed_version(long time)
    {
      if(commits.containsKey(time))
          return commits.get(time);
      return commits.get(commits.headMap(time).firstKey());
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
      int NUM_WRITERS = 5;

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

      long maxtime = 0;

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
          long time = 0;
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

              int staleness = maxversion-commits.last_committed_version(time);

              time += endtime;
          }
      }

      /*

    val lastCommitted = new AtomicInteger(0)
    val finishTimes = new ConcurrentHashMap[Int, Long]
    val commitTimes = new ConcurrentHashMap[Int, Long]
    val readOutputs = Collections.synchronizedList(new ArrayList[ReadOutput])

    var server = new KVServer(sendDelayFile, ackDelayFile)
    for (i <- 0 until 1000000)
      System.out.println(server.getReadAckDelay())

    val replicas = new ListBuffer[KVServer]
    for (i <- 0 until N+1) 
      replicas += new KVServer(sendDelayFile, ackDelayFile)

    val w = new Thread(new Writer(replicas.toList, 
        ITERATIONS, W, key, lastCommitted, finishTimes, commitTimes))


    val readerThreads = new ListBuffer[Thread]
    for (i <- 0 until NUM_READERS)
      readerThreads.append(new Thread(new Reader(replicas.toList, 
        ITERATIONS, R, key, lastCommitted, readOutputs)))

    w.start()
    Thread.sleep(2)
    for (reader <- readerThreads)
      reader.start()

    w.join()
    for (reader <- readerThreads)
      reader.join()

    for (r <- replicas.toList) r.join

    val readPlotValues = new ListBuffer[ReadPlot]
    for (r <- readOutputs) {
      val wCommitTime = commitTimes.getOrElse(r.version_at_start, -1): Long
      readPlotValues.append(new ReadPlot(r, wCommitTime))
    }

    var percentiles = new Range(900, 1000, 1)
    var reads = readPlotValues.sortBy(
      x => x.read.start_time - x.commit_time_at_start).reverse
    // Console.err.println("Number of reads " + reads.length)

    //println("Percentile " + LAMBDA)
    for (p <- percentiles) {
      var tstale: Long = 0
      var staler = 0
      var current = 0
      var tstaleComputed = false

      var pst: Double = (1-p/1000.0)

      var how_many_stale = Math.ceil(reads.length*pst) 
      for (r <- reads) {
        if (r.read.version_read >= r.read.version_at_start)
          current = current + 1
        else
          staler = staler + 1

        if (staler > how_many_stale && !tstaleComputed) {
          tstaleComputed = true
          tstale = r.read.start_time - r.commit_time_at_start
        }
      }
      //println(p + " " + tstale)
    }
    
    // val tStaleness = new ListBuffer[Long]
    // Calculate t-visibility stalness for each read
    // for (r <- readStartTimes) {
    //   val wFinishTime = finishTimes.getOrElse(r._1, -1): Long
    //   if (wFinishTime - r._2 < 0) 
    //     println("wFinishTime " + wFinishTime + " read start " + r._2 + 
    //       " key " + r._1)
    //   else 
    //     tStaleness.append(wFinishTime - r._2) 
    // }
    // println("Avg t-staleness " + tStaleness.sum.toDouble /
    //  tStaleness.length.toDouble)

    // For each read
    exit(0)
    */
  }
}
