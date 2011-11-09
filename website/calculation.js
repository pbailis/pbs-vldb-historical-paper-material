
function calc_exponential_pdf(lmbda, t)
{
    return lmbda*Math.exp(-lmbda*t);
}

function calc_exponential_cdf(lmbda, t)
{
    return 1-Math.exp(-lmbda*t);
}

//Rosetta code ftw
function binom(n, k) {
    var coeff = 1;
    for (var i = n-k+1; i <= n; i++) coeff *= i;
    for (var i = 1;     i <= k; i++) coeff /= i;
    return coeff;
}

function calc_p_s_given_w(R, W, N)
{
   if(R+W>N)
	return 1.0;

    return binom(N-W, R)/binom(N, R);
}

function cdf_get_prob_w_after_write(curw, W, t, lambda_w)
{
    return 1-Math.pow(1-Math.pow(calc_exponential_cdf(lambda_w, t), curw-W), binom(N-W, curw-W));
}

function calc_prob_stale(R, W, N, t, k, lambda_ack)
{
    if(R+W>N)
	return 1.0;

    var ret = calc_p_s_given_w(R, W, N);

    for(int w = W; w < N; ++1)
    {
	ret += ((calc_p_s_given_w(R, w+1)-
		 calc_p_s_given_w(R, w))
		*cdf_get_prob_w_after_write(w+1, W, t, lambda_w));
    }

    return ret;
}