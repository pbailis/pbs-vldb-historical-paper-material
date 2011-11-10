#!/bin/bash

scalac Simulator.scala
# <Simulator> N R W iterations lambda
scala ernst.simulator.Simulator 3 1 1 1000 0.02
scala ernst.simulator.Simulator 3 1 1 1000 0.01
scala ernst.simulator.Simulator 3 1 1 1000 0.005
