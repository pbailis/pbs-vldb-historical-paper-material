#!/bin/bash

scalac Simulator.scala
# <Simulator> N R W iterations lambda
for lambda in 0.002 0.005 0.01 0.05 0.1
do
  scala ernst.simulator.Simulator 3 1 1 3000 $lambda > data-points-$lambda.out
done

#scala ernst.simulator.Simulator 3 1 1 1000 0.01
#scala ernst.simulator.Simulator 3 1 1 1000 0.005
