package ernst.simulator

import scala.collection.immutable.List
import scala.collection.mutable.ListBuffer
import scala.collection.mutable.HashMap
import scala.collection.JavaConversions._
import scala.util.Random
import java.util.concurrent._
import java.util.concurrent.atomic.AtomicInteger
import java.util.{ArrayList, Collections}
import java.util.Date
import java.lang.Math

import ernst.solver.FileLatencyModel

class ReadOutput (var version_at_start: Int, var version_read: Int,
                  var start_time: Long)
class ReadPlot (var read: ReadOutput, var commit_time_at_start: Long) 

class KVServer(writeF: String, readF: String, numThreads: Int) {
  private val kv: ConcurrentMap[Int, Int] = new ConcurrentHashMap[Int, Int]
  var rand = new Random()
  val MAX_DELAY = 20
  val exec = new ScheduledThreadPoolExecutor(numThreads)
  var writeLatencyModel = new FileLatencyModel(writeF)
  var readLatencyModel = new FileLatencyModel(readF)
  val LAMBDA = 0.05

  def getExpRandom() : Long = {
    return Math.round(Math.log(1-rand.nextDouble())/(-LAMBDA))
  }

  def getUniformRandom(): Long = {
    return rand.nextInt(MAX_DELAY)
  }

  def getWriteDelay(): Long = {
    return Math.round(writeLatencyModel.getInverseCDF(1,
        rand.nextDouble()))
  }
  def getReadDelay(): Long = {
    return Math.round(readLatencyModel.getInverseCDF(1,
        rand.nextDouble()))
  }

  // def getWriteAckDelay(): Long = {
  //   return Math.round(ackLatencyModel.getInverseCDF(1,
  //       rand.nextDouble()))
  // }
  // def getReadAckDelay(): Long = getWriteAckDelay

  def write(k: Int, v: Int, latch: CountDownLatch, 
      nlatch: CountDownLatch, m: ConcurrentMap[Int, Long]) = {
    var r = new Runnable() {
      def run = {
        var delay = getWriteDelay()
        Thread.sleep(delay/2)
        if (v > kv.getOrElse(k, 0))
          kv.put(k,v)
        nlatch.countDown()
        val fin = new Date().getTime();
        if (nlatch.getCount() == 0) {
          m.put(v, fin)
        }
        //println("write replica " + v + " finished at " + fin)
        Thread.sleep(delay/2)
        latch.countDown()
      }
    }
    exec.schedule(r, 0, TimeUnit.MILLISECONDS) 
  }

  def read(k: Int, latch: CountDownLatch) : ScheduledFuture[Int] = {
    var t = new Callable[Int]() {
      def call: Int = {
        try {
          var delay = getReadDelay()
          Thread.sleep(delay/2)
          val ret = kv.getOrElse(k, 0)
          // println("read " + ret + " at " + new Date().getTime())
          Thread.sleep(delay/2)
          return ret
        } finally {
          latch.countDown()
        }
      }
    }
    return exec.schedule(t, 0, TimeUnit.MILLISECONDS)
  }

  def join = {
    exec.shutdown()
    exec.awaitTermination(5, TimeUnit.SECONDS)
  }
}

class Writer(replicas: List[KVServer], numWrites: Int, W: Int, k: Int,
    lc:AtomicInteger, m: ConcurrentMap[Int, Long], 
    wf:ConcurrentMap[Int, Long]) extends Runnable {
  def run() = {
    for (i <- 0 until numWrites) {
      val latch = new CountDownLatch(W)
      val nlatch = new CountDownLatch(replicas.length)
      for (replica <- replicas) {
        replica.write(k, i, latch, nlatch, m)
      }
      latch.await()
      wf.put(i, new Date().getTime())
      lc.set(i)
      //println("Write " + i + " finished at " + new Date().getTime())
    }
  }
}

class Reader(replicas: List[KVServer], numReads: Int, R: Int, k: Int,
    lc: AtomicInteger, rs: java.util.List[ReadOutput]) extends Runnable {
  var staleReads = 0 
  var kStaleness = new ListBuffer[Int]
  def getFinalValue(futures: ListBuffer[ScheduledFuture[Int]]): (Int,Int) = {
      var finalValue = 0
      var numFinished = 0
      for (f <- futures) {
        if (f.isDone()) {
          numFinished = numFinished + 1
          if (f.get > finalValue)
            finalValue = f.get
        }
      }
      return (finalValue, numFinished)
  }
  def run() = {
    for (i <- 0 until numReads) {
      val lastCommitedAtStart = lc.get()
      val readStartTime = new Date().getTime()
      val latch = new CountDownLatch(R)
      val futures = new ListBuffer[ScheduledFuture[Int]]
      for (replica <- replicas) {
        futures.append(replica.read(k, latch))
      }
      latch.await()
      val finishTime = new Date().getTime()
      // R futures should have completed
      var tuple = getFinalValue(futures)
      var finalValue = tuple._1
      var numFinished = tuple._2

      while (numFinished < R) {
        // Race condition ? Try again 
        Console.err.println("Too few futures finished ! " + numFinished + " " + R)
        // Give it a millisecond to make sure
        Thread.sleep(1)
        var tuple = getFinalValue(futures)
        finalValue = tuple._1
        numFinished = tuple._2
      }
      if (finalValue < lastCommitedAtStart) {
        staleReads = staleReads + 1
        kStaleness += (lastCommitedAtStart - finalValue)
        // println("Expected " + lastCommitedAtStart + " got " +
        //     finalValue)
      }
      rs.add(new ReadOutput(
        lastCommitedAtStart, finalValue, readStartTime))
      //println("Read " + i + " finished at " + finishTime + " value " +
      //    finalValue + " lc at start " + lastCommitedAtStart)
    }
    // Console.err.println("Stale reads " + staleReads)
    // println("Reads total: " + numReads + " stale: " + staleReads)
    // println("Avg k-staleness " + 
    //   kStaleness.sum.toDouble/kStaleness.length.toDouble)
  }
}

object Simulator {
  var N = 3
  var W = 2
  var R = 1
  var ITERATIONS = 100 
  var writeDelayFile: String = ""
  var readDelayFile: String = ""
  val key = 100
  val NUM_READERS = 15

  def main (args: Array[String]) {
    args match {
      case Array(n, r, w, iters, writeF, readF) => {
        N = n.toInt
        R = r.toInt
        W = w.toInt
        ITERATIONS = iters.toInt
        writeDelayFile = writeF
        readDelayFile = readF
      }
      case _ => {
        System.err.println(
          "Usage: Simulator <N> <R> <W> <iters> <sendF> <ackF>")
        System.exit(1)
      }
    }
    val lastCommitted = new AtomicInteger(0)
    val finishTimes = new ConcurrentHashMap[Int, Long]
    val commitTimes = new ConcurrentHashMap[Int, Long]
    val readOutputs = Collections.synchronizedList(new ArrayList[ReadOutput])

    val replicas = new ListBuffer[KVServer]
    for (i <- 0 until N+1) 
      replicas += new KVServer(writeDelayFile, readDelayFile, NUM_READERS*2)

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
      println(p + " " + tstale)
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
  }
}
