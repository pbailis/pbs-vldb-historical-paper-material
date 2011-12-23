#!/bin/bash

# Extract latency profiles
pushd ../graph_scripts
python latency_profiles_for_simulator.py
popd

DIR="../graph_scripts/analyzedir-"
NUM_WRITES=3000

scalac -cp nrwsolver.jar Simulator.scala

# <Simulator> N R W iterations <send-dist> <ack-dist>

for lambda in 0.002000 0.005000 0.010000 0.050000 0.100000
do
  scala -cp nrwsolver.jar ernst.simulator.Simulator 3 1 1 $NUM_WRITES $DIR$lambda/wlatency.dist $DIR$lambda/rlatency.dist > data-points-5-readers-$lambda.out
done

TMP_1="/tmp/a"
TMP_2="/tmp/b"
MERGED=data-points-merged-5-readers.out
PDF=t_cdf.pdf

cp data-points-5-readers-0.002000.out $TMP_1

for lambda in 0.005000 0.010000 0.050000 0.100000
do
  join $TMP_1 data-points-5-readers-$lambda.out > $TMP_2
  TMP=$TMP_1
  TMP_1=$TMP_2
  TMP_2=$TMP
done

cp $TMP_1 $MERGED

sed -i '1i\Perc 0.002 0.005 0.01 0.05 0.1' $MERGED
./plot_t_cdf.gpl $MERGED $PDF
