
var CALC_ITERATIONS = 2500.0;
var MAX_PS = 1-1/CALC_ITERATIONS;

function update_max_iterations(its)
{
    CALC_ITERATIONS = its;
    MAX_PS = 1-1/CALC_ITERATIONS;
}

function calc_exponential_pdf(lmbda, t)
{
    return lmbda*Math.exp(-lmbda*t);
}

function calc_exponential_cdf(lmbda, t)
{
    return 1-Math.exp(-lmbda*t);
}

function calc_exponential_expected(lmbda)
{
    return 1/lmbda;
}

function roundNumber(num, dec) {
	var result = Math.round(num*Math.pow(10,dec))/Math.pow(10,dec);
	return result;
}

function nextExponential(lmbda)
{
    return Math.log(1-Math.random())/(-lmbda);
}

function sortfloats(l)
{
    return l.sort(function(a,b){return a - b});
}

function calculate_operation_latency(N, waitfor,  l1, l2)
{
    var ITERATIONS = 1000.0;
    var i = 0;
    lats = 0;
    for(i = 0; i < ITERATIONS; i++)
    {
	var round = [];
	for(r=0; r < N; ++r)
	{
	    round.push(nextExponential(l1)+nextExponential(l2));
	}
	lats += sortfloats(round)[waitfor-1];
    }
    
    return roundNumber(lats/ITERATIONS, 2);
}

function calc_prob_stale(N,R,W,Wl, Al, Rl, Sl, t, k)
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
	    var thisW = nextExponential(Wl);
	    var thisA = nextExponential(Al);
	    
	    Ws.push(thisW);
	    As.push(thisA);
	    writelats.push(thisW+thisA);

	    var thisR = nextExponential(Rl);
	    var thisS = nextExponential(Sl);

	    Rs.push(thisR);
	    Ss.push(thisS);
	    readlats.push(thisR+thisS);
	}

	var w_t = sortfloats(writelats)[W-1];

	//total hack, terrible big O, but N is small...
	var sortedreads = sortfloats(readlats.slice(0));

	for(rep = 0; rep < R; ++rep)
	{
	    //find the ith fastest read
	    var repNo = readlats.indexOf(sortedreads[rep]);

	    if(w_t + Rs[repNo]+t >= Ws[repNo])
	    {
		currents++;
		break;
	    }

	    //in the unlikely event of dups, delete
	    delete readlats[repNo];
	} 
    }

    return Math.pow(currents/CALC_ITERATIONS, k);
}