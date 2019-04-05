#########################################################################################################################################################################
# Author : Remi Monthiller, remi.monthiller@etu.enseeiht.fr
# Adapted from the code of Raphael Maurin, raphael.maurin@imft.fr
# 30/10/2018
#
# Incline plane simulations
#
#########################################################################################################################################################################

# import lib
import os
import matplotlib.pyplot as plt

# import params
execfile('params.py')

# Simulation
datas = os.listdir("data")
if datas:
	for i in range(len(datas)):
		datas[i] = float(datas[i].split(".yade")[0])
	datas.sort()
	# import PyRunners
	execfile('../common_test/simulationPyRunners.py')
	O.load("data/"+str(datas[-1])+".yade")
	#O.run()
else:
	# import simulation
	execfile('framework.py')
	execfile('../common_test/simulationDefinition.py')
	simulation()
