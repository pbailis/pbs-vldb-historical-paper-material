TMP_1="/tmp/a"
TMP_2="/tmp/b"
MERGED=data-points-merged.out

cp data-points-0.002.out $TMP_1

for lambda in 0.005 0.01 0.05 0.1
do
  join $TMP_1 data-points-$lambda.out > $TMP_2
  TMP=$TMP_1
  TMP_1=$TMP_2
  TMP_2=$TMP
done

cp $TMP_1 $MERGED
