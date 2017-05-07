from math import ceil


	
def rk_step(x,t,h,f):
	k1 = f(x,t)
	k2 = f(x+map(lambda x: x*(h/2.0),k1),t+(h/2.0))
	k3 = f(x+map(lambda x: x*(h/2.0),k2),t+(h/2.0))
	k4 = f(x+map(lambda x: x*h,k3),t+h)

	x_next = [0]*len(x)
	
	for i in range(0,len(x)):
		x_next[i] = x[i] + h*((1/6.0)*k1[i]+ (1/3.0)*k2[i]+(1/3.0)*k3[i]+(1/6.0)*k4[i])
		
	return x_next

def rk(x0,t0,t1,h,f):
	steps = int(ceil((t1-t0)/h))

	if steps < 100:
		print "Warning less than 100 simulation steps: {0}".format(steps)
	trace = [(x0,t0)]
	i = 0
	for i in range(0,steps):
		x = trace[i][0]
		t = trace[i][1]
		trace.append((rk_step(x, t, h,f),t+h))
	
	return trace

if __name__ == "__main__":

		trace = rk([5], 0,1e-3, 1.0)
		print trace


