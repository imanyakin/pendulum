#!/usr/bin/env python
import matplotlib.pyplot as plt 
import numpy as np

def plot_point(ax,x,y):
	points, = ax.plot(x,y,marker='o',linestyle='None')
	return points


def xy_animate(traces,xlims,ylims,duration):

	
	#configure plot
	fig, ax = plt.subplots()
	ax.set_xlim(xlims[0], xlims[1])
	ax.set_ylim(ylims[0], ylims[1]) 

	datapoint_count = len(traces[0][0])
	traces.append([[0]* datapoint_count,[0]* datapoint_count])
	#get number of steps
	datapoint_count = len(traces[0][0])
	points = [0]*len(traces)
	

	
	
	for i in range(0, datapoint_count):
		for t in range(0,len(traces)):
			x = traces[t][0][i]
			y = traces[t][1][i]
			
			if i == 0:
				points[t], = ax.plot(x, y, marker='o', linestyle='None')
			else:
				points[t].set_data(x, y)


		plt.pause(float(duration)/datapoint_count)

