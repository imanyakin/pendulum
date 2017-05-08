#!/usr/bin/env python

import csv, os, inspect,sys,io, argparse
from dateutil import parser
import matplotlib.pyplot as plt
from matplotlib.pyplot import ion
import numpy as np
import multiprocessing as mp
from multiprocessing import Process
import datetime

imageExtension = "png"

def decode(row):
    
    fields = ["timestamp", "stack_name", "lifetime", "maxCapacity", "queue", "messages", "currentTarget", "fulfilled", "newTarget"]
    if len(fields) != len(row):
        raise ValueError("Ops! Looks like len(fields)!=len(row), indicates format has changed!")
    else:
        outp= dict()
        for i in range(0,len(row)):
            outp.update({fields[i]:row[i]})
        
        return outp

def tdiff(xs):
    outp = [xs[k]-xs[k-1] for k in range(1,len(xs))]
    return outp
def tsum(xs):
    outp = [xs[k]+xs[k-1] for k in range(1,len(xs))]
    return outp
  
def hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h,24)
    return int(d),int(h),int(m),int(s)
    
def process_file(logfile):
    
    logfileHandle = io.open(logfile)
    csvfile = csv.reader(logfileHandle)
    
    data = dict()
    
    for row in csvfile:
        
        decoded_row = decode(row)
        stack_name = decoded_row["stack_name"]
        qname = decoded_row["queue"]
        timestamp = parser.parse(decoded_row["timestamp"])
        if decoded_row["stack_name"] not in data.keys():
            data.update({stack_name : dict()})
            
        usedValues = ["messages", "currentTarget", "fulfilled", "newTarget","queue"]
        data[stack_name].update({timestamp: {k:v for k,v in decoded_row.iteritems() if k in usedValues}})
        
        
    return data,qname

def custom_plots(plt,xs,ys,data,lefty,righty):
    
    dy = tdiff(ys["fulfilled"]["data"])
    dy.insert(0,0)
    dy=[y if y >0 else 0 for y in dy]
    ys.update({"bought":        {"data":dy, "axes":lefty, "linestyle":"--", "colour": "purple", "plot":""}})
    for k in ["bought"]:
        y = ys[k]["data"]
        ax = ys[k]["axes"]
        ph = ax.plot(xs,y,label=k, marker=".",linestyle=ys[k]["linestyle"], color=ys[k]["colour"])
        ys[k]["plot"] = ph[0] 

def integrate(xs,ys):
    if isinstance(xs[0],int):
        sum_terms = [((ys[k+1]+ys[k])/2.0)*(xs[k+1]-x[k]) for k in range(0,len(xs)-1)]
    elif isinstance(xs[0],datetime.date):
        sum_terms = [((ys[k+1]+ys[k])/2.0)*((xs[k+1]-xs[k]).seconds) for k in range(0,len(xs)-1)]
    else:
        raise ValueError("Unknown type")
    return sum(sum_terms)



def plot_data(data, stack_name,qname,save=False, interactive=False):
    xs = sorted(data[stack_name].keys())
    dx = max(xs)- min(xs)
    ys = dict()
    fig, lefty = plt.subplots(figsize=(12,9))
    righty = lefty.twinx()
    lefty.set_xlabel("Time (/s)")
    lefty.set_ylabel("Capacities (/spot unit)")
    righty.set_ylabel("Messages (/count)")
    plt.xlim(min(xs) -dx/10, max(xs)+dx/10)
    lefty.grid(True)

    ys.update({"currentTarget": {"data":[], "axes":lefty, "linestyle":"-", "colour": "red",    "plot":""}})
    ys.update({"fulfilled":     {"data":[], "axes":lefty, "linestyle":"-", "colour": "blue",   "plot":""}})
    ys.update({"newTarget":     {"data":[], "axes":lefty, "linestyle":"-", "colour": "green",  "plot":""}})
    ys.update({"messages":      {"data":[], "axes":righty,"linestyle":"-", "colour": "orange", "plot":""}})
        
    #Pure time series data 
    for k in ys.keys():
        ys[k]["data"] = [int(data[stack_name][x][k]) for x in xs]
        y = ys[k]["data"]
        ax = ys[k]["axes"]
        ph = ax.plot(xs,y,label=k, marker=None,linestyle=ys[k]["linestyle"], color=ys[k]["colour"])
        ys[k]["plot"] = ph[0]
        
    #Compound time series data
    custom_plots(plt, xs,ys, data,lefty,righty)
    plt.legend(handles=[ys[k]["plot"] for k in ys.keys()], loc='upper left')
    
    plt.gcf().autofmt_xdate()
    
    singleCoreSeconds = integrate(xs,ys["fulfilled"]["data"])
    days,hours,minutes,seconds = hms(singleCoreSeconds)
    
    
    tstr = []
    tstr.append("Queue:{0}\n".format(qname))
    tstr.append("Stack:{0}\n".format(stack_name))
    tstr.append("Time:{0} - {1}\n".format(min(xs).replace(microsecond=0), max(xs).replace(microsecond=0)))
    tstr.append("Bought units:{0}\n".format(sum(ys["bought"]["data"])))
    tstr.append("Executing time: Days({0}),Hours({1}),Minutes({2}),Seconds({3})".format(days,hours,minutes,seconds))
    for t in tstr:
        print t
    
    plt.title("".join(tstr[0:5]),fontsize=12)
    if save:
        cwd = os.getcwd()
        path = cwd+"/plot_{0}.{1}".format(stack_name,imageExtension)
        print "Saving image to: {0}".format(path)
        
        plt.savefig(path)
    if interactive:
        plt.show()


            
def main(argv):
    parser = argparse.ArgumentParser(description='Admin-helper launcher, minimum arguments to specify: target ini file of workflows')
    parser.add_argument("logfile", help ="path to file containing logs")
    parser.add_argument("-n","--name",dest="stack_name", help = "Id of fleet you want to display", default=None)
    parser.add_argument("-s","--save",dest="save",action="store_true", help = "flag to save image")
    parser.add_argument("-i","--interactive",dest="interactive",action="store_true", help = "interactive graph")
    parser.add_argument("-l","--list",dest="list",action="store_true", help = "list stack names and exit")
    args =  parser.parse_args()
    
    #resolve filepath from current directory
    
    args.logfile = os.getcwd()+"/"+args.logfile
    
    data,qname = process_file(args.logfile)    
    if args.stack_name == None:
        print("-----Stack Names-----")
        for k in data.keys():
            print k

        if args.list:
            return
        args.stack_name = raw_input("Please enter a stack_name or exit: ")
        if args.stack_name == "Exit" or args.stack_name == "exit":
            return
    
    if args.stack_name not in data.keys():
        #Print: No such fleet id, exit
        print "No such fleet id found, terminating..."
        return
    
    
    plot_data(data,args.stack_name,qname,save=args.save, interactive=args.interactive)
    
    

         
if __name__ == "__main__":
    main(sys.argv[1:])




