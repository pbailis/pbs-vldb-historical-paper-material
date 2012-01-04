
/*
  These functions serve as reference implementations for using PBS.
  The first calculates PBS <k,t>-staleness and the second calculates
  expected read and write latencies.  Both are implemented using Monte
  Carlo analysis.
*/

/*
  This function calculates the probability that a read will return one
  of the last k committed values t seconds after the last value commits
  for Dynamo-style replication without read repair.

  N: number of replicas
  R: number of read responses to wait for before returning
  W: number of write responses to wait for before committing

  {W, A, R, S}_lambda: parameters describing the message delays In
  this implementation, they're exponentially distributed, but this
  need not be the case.  See the paper or the site for more
  description of the WARS model.

  t: time after last write

  k: number of versions of staleness tolerable

  This analysis is conservative in that it assumes that the last k
  versions completed at the same time.  In practice, they're likely
  staggered.

  Helper functions are in calculate-misc.js.
*/

function calc_prob_stale(N,R,W,W_lambda, A_lambda, R_lambda, S_lambda, t, k)
{
    var currents = 0;

    var i = 0;
    for(i = 0; i < CALC_ITERATIONS; i++)
    {
	var Ws = [];
	var As = [];
	var writelats = [];
	var Rs = [];
	var Ss = [];
	var readlats = [];

	var rep = 0;
	for(rep = 0; rep < N; ++rep)
	{
	    var thisW = nextExponential(W_lambda);
	    var thisA = nextExponential(A_lambda);
	    
	    Ws.push(thisW);
	    As.push(thisA);
	    writelats.push(thisW+thisA);

	    var thisR = nextExponential(R_lambda);
	    var thisS = nextExponential(S_lambda);

	    Rs.push(thisR);
	    Ss.push(thisS);
	    readlats.push(thisR+thisS);
	}

	//the write takes as long as the Wth response
	var w_t = sortfloats(writelats)[W-1];

	//slice() copies the readlats array
	var sortedreads = sortfloats(readlats.slice());

	for(rep = 0; rep < R; ++rep)
	{
	    //find the ith fastest read
	    var repNo = readlats.indexOf(sortedreads[rep]);
	    
	    //if one of the first R reads came from a replica that had received the
	    //last write, the read was consistent
	    if(w_t + Rs[repNo]+t >= Ws[repNo])
	    {
		currents++;
		break;
	    }

	    //in the unlikely event of dups, delete
	    delete readlats[repNo];
	} 
    }

    //k versions of staleness (assuming independence--see paper) are like k separate
    //intersection events, so simply exponentiate
    return 1-Math.pow((CALC_ITERATIONS-currents)/CALC_ITERATIONS, k);
}

/*
  This functions calculate a given percentile latency of read/write operations.

  The parameters are as above.
*/

function calculate_write_latency(N, W, W_lambda, A_lambda, pctile)
{
    return calculate_operation_latency(N, W, W_lambda, A_lambda, pctile);
}

function calculate_read_latency(N, R, R_lambda, S_lambda, pctile)
{
    return calculate_operation_latency(N, R, R_lambda, S_lambda, pctile);
}

function calculate_operation_latency(N, waitfor, lambda1, lambda2, pctile)
{
    var ITERATIONS = Math.max(10000.0, 1/(1-pctile))
    var i = 0;
    lats = 0;
    var latencies = []
    for(i = 0; i < ITERATIONS; i++)
    {
	var round = [];
	for(r=0; r < N; ++r)
	{
	    //calculate RTTs for each of the replicas
	    round.push(nextExponential(lambda1)+nextExponential(lambda2));
	}
	//the latency of this operation is the <waitfor>th fastest
	latencies.push(sortfloats(round)[waitfor-1]);
    }

    return sortfloats(latencies)[ITERATIONS*pctile];
}