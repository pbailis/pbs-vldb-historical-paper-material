package ernst.simulator

import scala.collection.immutable.List
import scala.collection.mutable.ListBuffer
import scala.collection.mutable.HashMap
import scala.collection.JavaConversions._
import scala.util.Random
import java.util.concurrent._
import java.util.concurrent.atomic.AtomicInteger
import java.util.Date
import java.lang.Math

class ReadOutput (var version_at_start: Int, var version_read: Int,
                  var start_time: Long)
class ReadPlot (var read: ReadOutput, var commit_time_at_start: Long) 

class KVServer(lambda: Double) {
  private val kv: ConcurrentMap[Int, Int] = new ConcurrentHashMap[Int, Int]
  var rand = new Random()
  val MAX_DELAY = 20
  val exec = new ScheduledThreadPoolExecutor(10)

  def getExpRandom() : Long = {
    return Math.round(Math.log(1-rand.nextDouble())/(-lambda))
  }

  def getUniformRandom(): Long = {
    return rand.nextInt(MAX_DELAY)
  }

  def write(k: Int, v: Int, latch: CountDownLatch, 
      nlatch: CountDownLatch, m: ConcurrentMap[Int, Long]) = {
    var r = new Runnable() {
      def run = {
        Thread.sleep(getExpRandom())
        if (v > kv.getOrElse(k, 0))
          kv.put(k,v)
        nlatch.countDown()
        val fin = new Date().getTime();
        if (nlatch.getCount() == 0) {
          m.put(v, fin)
        }
        //println("write replica " + v + " finished at " + fin)
        Thread.sleep(getExpRandom())
        latch.countDown()
      }
    }
    exec.schedule(r, 0, TimeUnit.MILLISECONDS) 
  }

  def read(k: Int, latch: CountDownLatch) : ScheduledFuture[Int] = {
    var t = new Callable[Int]() {
      def call: Int = {
        try {
          Thread.sleep(getExpRandom())
          val ret = kv.getOrElse(k, 0)
          // println("read " + ret + " at " + new Date().getTime())
          Thread.sleep(getExpRandom())
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
    lc: AtomicInteger, rs: ListBuffer[ReadOutput]) extends Runnable {
  var staleReads = 0 
  var kStaleness = new ListBuffer[Int]
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
      var finalValue = 0
      var numFinished = 0
      // R futures should have completed
      // Give it a millisecond to make sure
      for (f <- futures) {
        if (f.isDone()) {
          numFinished = numFinished + 1
          if (f.get > finalValue)
            finalValue = f.get
        }
      }
      if (numFinished < R) {
        // Race condition ? Ignore ? 
        Console.err.println("Too few futures finished !" + numFinished + " " + R)
      }
      if (finalValue < lastCommitedAtStart) { 
        staleReads = staleReads + 1
        kStaleness += (lastCommitedAtStart - finalValue)
        // println("Expected " + lastCommitedAtStart + " got " +
        //     finalValue)
      }
      rs.append(new ReadOutput(
        lastCommitedAtStart, finalValue, readStartTime))
      //println("Read " + i + " finished at " + finishTime + " value " +
      //    finalValue + " lc at start " + lastCommitedAtStart)
    }
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
  var LAMBDA = 0.05
  val key = 100

  def main (args: Array[String]) {
    args match {
      case Array(n, r, w, iters, lambda) => {
        N = n.toInt
        R = r.toInt
        W = w.toInt
        ITERATIONS = iters.toInt
        LAMBDA = lambda.toDouble
      }
      case _ => {
        System.err.println("Usage: Simulator <N> <R> <W> <iters> <lambda>")
        System.exit(1)
      }
    }
    val lastCommitted = new AtomicInteger(0)
    val finishTimes = new ConcurrentHashMap[Int, Long]
    val commitTimes = new ConcurrentHashMap[Int, Long]
    val readOutputs = new ListBuffer[ReadOutput]

    val replicas = new ListBuffer[KVServer]
    for (i <- 0 until N+1) replicas += new KVServer(LAMBDA)

    val w = new Thread(new Writer(replicas.toList, 
        ITERATIONS, W, key, lastCommitted, finishTimes, commitTimes))
    val r = new Thread(new Reader(replicas.toList, 
        ITERATIONS, R, key, lastCommitted, readOutputs))

    w.start()
    Thread.sleep(2)
    r.start()

    w.join()
    r.join()

    for (r <- replicas.toList) r.join

    val readPlotValues = new ListBuffer[ReadPlot]
    for (r <- readOutputs) {
      val wCommitTime = commitTimes.getOrElse(r.version_at_start, -1): Long
      readPlotValues.append(new ReadPlot(r, wCommitTime))
    }

    var percentiles = new Range(900, 1000, 1)
    var reads = readPlotValues.sortBy(
      x => x.read.start_time - x.commit_time_at_start).reverse

    println("Percentile " + LAMBDA)
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
