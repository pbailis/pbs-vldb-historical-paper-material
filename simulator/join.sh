TMP_1="/tmp/a"
TMP_2="/tmp/b"
MERGED=data-points-merged-real-5-readers.out

cp data-points-5-readers0.002000.out $TMP_1

for lambda in 0.005000 0.010000 0.050000 0.100000
do
  join $TMP_1 data-points-5-readers$lambda.out > $TMP_2
  TMP=$TMP_1
  TMP_1=$TMP_2
  TMP_2=$TMP
done

cp $TMP_1 $MERGED
