
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
