#!/usr/bin/env python

#from rk import *
import numpy as np
#from graphics import 
from imtools.graphics import xy_animate, plot_timeseries
#.xy_animate as xy_animate, graphics.plot_timeseries as plot_timeseries
from imtools.rk import rk

#integration functions
class DoublePendulum:

	def __init__(self,debug =0):
		#constants for pendulum	
		
		self.m1 = 1.0
		self.m2 = 1.0

		self.l1 = 1.0
		self.l2 = 1.0
		
		self.g = 9.81
		self.debug = debug

	def to_xy_point(self,theta1,theta2):

		x1 = self.l1*np.sin(theta1)
		x2 = x1 + self.l2*np.sin(theta2)
		y1= -self.l1*np.cos(theta1)
		y2 = y1 - self.l2*np.cos(theta2)

		return [x1,y1,x2,y2]


	def to_xy_trace(self,trace):
		#extract theta_1 and theta_2 from trace:
		theta_trace = [t[0][0:2] for t in trace]

		xy_trace = [self.to_xy_point(theta[0],theta[1]) for theta in theta_trace]

		x1s = [xy[0] for xy in xy_trace]
		y1s = [xy[1] for xy in xy_trace]
		x2s = [xy[2] for xy in xy_trace]
		y2s = [xy[3] for xy in xy_trace]

		l1s = [(x1s[i]**2 + y1s[i]**2)**0.5 for i in range(0,len(x1s))]
		l2s = [((x1s[i]-x2s[i])**2 + (y1s[i]-y2s[i])**2)**0.5  for i in range(0,len(x1s))]

		if self.debug >= 1:

			print "L1: MAX: {0}, MIN: {1}".format(max(l1s), min(l1s))
			print "L2: MAX: {0}, MIN: {1}".format(max(l2s), min(l2s))

		if self.debug >= 2:
			print "MASS-1(X): {0}".format(x1s)
			print "MASS-1(Y): {0}".format(y1s)

			print "MASS-2(X): {0}".format(x2s)
			print "MASS-2(Y): {0}".format(y2s)

		return [(x1s,y1s),(x2s,y2s)]

	def animate(self, traces,duration):
		max_radius = self.l1+self.l2
		xlims = (-1.2*max_radius, 1.2*max_radius)
		ylims = xlims
		xy_animate(traces, xlims, ylims,duration)

	def ode(self,theta,t):

		if type(theta) is not list:
			raise ValueError("RK function has received incorrect input type")
		
		#angular coordinates
		theta_x = [theta[0],theta[1]]
		#angular velocities
		theta_v = [theta[2],theta[3]]

		#matrix terms
		a_11 = (self.m1+self.m2)*self.l1
		a_12 = self.m2*self.l2*np.cos(theta_x[0]-theta_x[1])
		a_21 = self.m2*self.l1*np.cos(theta_x[0]-theta_x[1])
		a_22 = self.m2*self.l2
		b_1 = -self.g*(self.m1+self.m2)*np.sin(theta_x[0])-self.m2*self.l2*theta_v[1]*np.sin(theta_x[0]-theta_x[1])
		b_2 = self.m2*self.l1*theta_v[0]*np.sin(theta_x[0]-theta_x[1])-self.m2*self.g*np.sin(theta_x[1])

		A = np.matrix([[a_11,a_12],[a_21,a_22]])
		B = np.matrix([[b_1],[b_2]])
		inv_A = np.linalg.inv(A)

		#get output in matrix form
		result = inv_A*B
		#extract values from matrix
		outp =  theta_v + [a[0] for a in result.tolist()]
		
		if self.debug >= 2:
			print t

		if self.debug >= 3:
			# print "INPUT: {0}".format(theta)
			print "VALUES:"
			print "    A: [{:0.3g},{:1.3g}]\n".format(a_11,a_12),
			print "       [{:0.3g},{:1.3g}]\n".format(a_21,a_22),
			print "    b: [{:0.3g},{:1.3g}]".format(b_1,b_2)
			# print "OUTPUT: {0}".format(outp)
		return outp

def simulation(x0=[1.0,1.0,0.0,0.0], duration=100.0,h=1e-2):

	#initialize pendulum
	pendulum = DoublePendulum(debug=1)
	#run integration
	theta_trace =  rk(x0=x0,t0= 0.0,t1=duration,h=h,f=pendulum.ode)
	#extract time trace from theta_trace
	time_trace = [t[1] for t in theta_trace]
	#convert theta_1,theta_2 to x1,y1,x2,y2
	xy_trace = pendulum.to_xy_trace(theta_trace)
	return xy_trace, time_trace, pendulum


def animated_simulation(x0=[1.0,1.0,0.0,0.0], duration=100.0,h=1e-2, slow_factor=1.0):
	#####
	# slow_factor: how much to slow animation by
	#	default: 1.0 - real time

	#run simulation
	xy_trace, time_trace, pendulum = simulation(x0,duration, h)
	# animate
	pendulum.animate(xy_trace,slow_factor*duration)
	#return the traces
	return

def plotted_simulation(x0=[1.0,1.0,0.0,0.0], duration=100.0,h=1e-2):
	#run simulation
	xy_trace, time, _ = simulation(x0,duration, h)
	#extract lists: [(xs,ys)] into [x1s,y1s,x2s,y2s,...]
	series_data = [series for xy in xy_trace for series in xy]
	# plot time series
	plot_timeseries(
		time,
		series_data,
		xlims=[min(time), 1.2*max(time)], 
		ylims=[1.2*min([min(ys) for ys in series_data]), 1.2*max([max(ys) for ys in series_data])]
	)

if __name__ == "__main__":

	animated_simulation()
	#plotted_simulation()
