import os
import sys
import matplotlib.pyplot as plt


#-------------------#
# Constants
#-------------------#
bigSep = "\n====================== "
sep = "---------------------- "

#-------------------#
# Variables
#-------------------#
colors = []
d_ad = 0

#-------------------#
# Setting plt options for latex
#-------------------#
plt.rc('text', usetex=True)

#-------------------#
# Getting names
#-------------------#
name_list = sys.argv[1]
name_list = name_list.split("_")
name_case = name_list[0]
for s in name_list[1:-2]:
	name_case += "-" + s
if len(name_list) > 2:
	name_param = name_list[-2]
	name_value = name_list[-1]
else:
	name_param = ""
	name_value = ""

#-------------------#
# Defining utils
#-------------------#
def color_gradient(grad_nb, p):
	p.colors = []
	for i in range(grad_nb):
		c = (i/float(grad_nb))
		p.colors.append((p.r[0]*c+p.r[1]*(1-c), p.v[0]*c+p.v[1]*(1-c), p.b[0]*c+p.b[1]*(1-c)))

def average(qT, t):
	""" Average qT over time.

	Parameters:
	- qT : Contains the quantity. : List of floats.
	"""
	n_time = len(t) - 1
	# Finding the first value to take into account.
	i_deb = 0
	while stime[i_deb] < pPP.mean_begin_time:
		i_deb += 1
	if i_deb > n_time - 1:
		print('WARNING average: End of simulation before start of averaging.')
		print('WARNING average: Taking only last profile.')
		i_deb = n_time - 1
	# Initialisation
	q = qT[i_deb]
	# Averaging
	i = i_deb + 1
	while i < n_time + 1 and t[i] < pPP.mean_end_time:
		q += qT[i]
		i += 1
	q /= (i - i_deb)
	return q

def average_profile(qT, t, n=False):
	""" Average qT profiles over time.

	Parameters:
	- qT : Contains all the profiles. : List of lists.
	qT[k][0] should correspond to the abscissa.
	- n : Enable normalise (for histograms) : bool
	"""
	n_time = len(t) - 1
	# Finding the first value to take into account.
	i_deb = 0
	while i_deb < len(t) and t[i_deb] < pPP.mean_begin_time:
		i_deb += 1
	if i_deb > n_time - 1:
		print('WARNING average_profile: End of simulation before start of averaging.')
		print('WARNING average_profile: Taking only last profile.')
		i_deb = n_time - 1
	# Initialisation
	q = []
	for l in qT[i_deb]:
		q.append(l[:])
	# Averaging
	i = i_deb + 1
	while i < n_time + 1 and t[i] < pPP.mean_end_time:
		for j in range(1, len(q)):
			for k in range(len(q[j])):
				q[j][k] += qT[i][j][k]
		i += 1
	if n:
		for j in range(1, len(q)):
			summ = sum(q[j])
			q[j] = [v/summ for v in q[j]]
	else:
		for j in range(1, len(q)):
			q[j] = [v/(i - i_deb) for v in q[j]]
	return q

def adim(q, star):
	""" non-dimensionalize the quantitie q by star.

	Parameters:
	- q : list
	- star : float
	"""
	return [a/star for a in q]

def integration(phi, y, dx):
	""" Integrate y along x ponderate by phi.

	"""
	q = 0
	for j in range(len(y)):
		q += phi[j] * y[j] * dx 
	
	return q

#-------------------#
# Import measures functions
#-------------------#
execfile("params_post_proc.py")
color_gradient(len(sys.argv) - 1, pP1D)
execfile("common/simulationPyRunners.py")
execfile("common/measures.py")

def read_ids(dr):
	print(sep + "Reading ids.")
	f = open(dr + '/.ids','r')
	ids = eval(f.read())
	f.close()
	return ids

def read_data(dr):
	print(sep + "Loading data.")
	stime = []
	data = {}
	for key in pP1D.measures:
		data[key] = []
	for f in os.listdir(dr+"/data"):
		print("Loading file: "+dr+"/data/" + f)
		### Loading data.
		O.load(dr+"/data/" + f)
		### Getting time.
		stime.append(O.time)
		### Measure data.
		for key in pP1D.measures: 
			data[key].append(eval(pP1D.measures[key]))
	return stime, data

def sort_data(stime, data):
	print(sep + "Sorting data.")
	for key in data:
		stime, data[key] = zip(*sorted(zip(stime, data[key])))
	return stime, data

def post_process(dr):
	# Update name_value
	name_value = dr.split("_")[-1]

	ids = read_ids(dr)
	stime, data = read_data(dr)
	stime, data = sort_data(stime, data)
	# Adding time to data
	data["time"] = stime
	# Post Processing
	for p in pP1D.post_process:
		for key in p:
			data[key] = eval(p[key])
	
	### Storing 2D data
	batch_val = eval(pP2D.param)
	if not (batch_val in batch_data):
		batch_data[batch_val] = {}
		for key in pP2D.measures:
			batch_data[batch_val][key] = []
	if pP2D.plot_enable:
		for key in pP2D.measures:
			batch_data[batch_val][key].append(eval(pP2D.measures[key]))
	
	### Ploting 1D data
	if pP1D.plot_enable:
		m = pP1D.markers.pop()
		c = pP1D.colors.pop()
		### Ploting figures
		print(sep + "Ploting data.")
		# Plots
		for key in pP1D.plots:
			for x in pP1D.plots[key][0]:
				me = int(max(1.0, pP1D.me * len(x)))
				for y in pP1D.plots[key][1]:
					axs[key].plot(data[x], data[y], color=c, marker=m, markevery=me,
							markerfacecolor=c, markeredgewidth=pP1D.mew, 
							markersize=pP1D.ms, label=r"$"+name_param+"="+name_value+"$")

#-------------------#
# Creating 1D Figures
#-------------------#
if pP1D.plot_enable:
	figs = {}
	axs = {}
	for key in pP1D.plots:
		figs[key] = plt.figure()
		axs[key] = plt.gca()
		plt.xlabel(pPP.plots_names[pP1D.plots[key][0][0]])
		plt.ylabel(pPP.plots_names[pP1D.plots[key][1][0]])

# Declaring batch data storage
batch_data = {}

#-------------------#
# Post Processing 1D
#-------------------#
for dr in sys.argv[1:]:
	print(bigSep + dr)
	os.chdir(dr)
	execfile("params.py")
	os.chdir("..")
	d_ad = eval(pPP.d_ad)
	post_process(dr)

#-------------------#
# Post Processing 2D
#-------------------#
if pP2D.plot_enable:
	### Computing Colors
	color_gradient(len(sys.argv) - 1, pP2D)
	
	### Sorting data
	params = []
	params_val = []
	for p, v in batch_data.items():
		params.append(p)
		params_val.append(v)
	params, params_val = zip(*sorted(zip(params, params_val)))

	for key in pP2D.plots:
		plt.figure()
		plt.xlabel(pPP.plots_names[pP2D.plots[key][0][0]])
		plt.ylabel(pPP.plots_names[pP2D.plots[key][1][0]])
		# Plotting
		batch_colors = colors[:]
		batch_markers = pP2D.markers[:]
		for i in range(len(params)):
			p = params[i]
			v = params_val[i]
			m = batch_markers.pop()
			c = batch_colors.pop()
			for x in pP2D.plots[key][0]:
				me = int(max(1.0, pP2D.me * len(x)))
				for y in pP2D.plots[key][1]:
					plt.plot(v[x], v[y], color=c, marker=m, markevery=me, markeredgewidth=pP2D.mew, markerfacecolor=c, markersize=pP2D.ms, label=r"$"+pPP.batch_param_name+"="+str(p)+"$")
					plt.legend(fancybox=True, framealpha=0.5)
					if pPP.save_figs:
						plt.savefig(pPP.save_fig_dir+name_case+"_"+pPP.batch_param_name+"_"+"qs(shields)"+".pdf")
	
	##### Creating rectangular patch to show averaging
	#if pPP.mean_over_time_enable:
	#	rect = plt.Rectangle((pPP.mean_begin_time, 0.0), pPP.mean_end_time - pPP.mean_begin_time, 1000, facecolor='w', edgecolor='k', hatch='/', alpha=0.3)
	#	axs["qs"].add_patch(rect)
	#	rect2 = plt.Rectangle((pPP.mean_begin_time, 0.0), pPP.mean_end_time - pPP.mean_begin_time, 1000, facecolor='w', edgecolor='k', hatch='/', alpha=0.3)
	#	axs["sh"].add_patch(rect2)
	#	rect3 = plt.Rectangle((pPP.mean_begin_time, 0.0), pPP.mean_end_time - pPP.mean_begin_time, 1000, facecolor='w', edgecolor='k', hatch='/', alpha=0.3)
	#	axs["qf"].add_patch(rect3)

if pP1D.plot_enable:
	## Adding legends
	for key in axs:
		axs[key].legend(fancybox=True, framealpha=0.5)

	### Converting xlabel with radian writing
	#axs["rotx"].set_xticklabels([r"$" + format(r/np.pi, ".2g")+ r"\pi$" for r in axs["rotx"].get_xticks()])
	#axs["roty"].set_xticklabels([r"$" + format(r/np.pi, ".2g")+ r"\pi$" for r in axs["roty"].get_xticks()])
	#axs["rotz"].set_xticklabels([r"$" + format(r/np.pi, ".2g")+ r"\pi$" for r in axs["rotz"].get_xticks()])
	
	### Saving figures
	if pPP.save_figs:
		for key in figs:
			figs[key].savefig(pPP.save_fig_dir+name_case+"_"+name_param+"_"+key+".pdf")

### Showing figures
plt.show()