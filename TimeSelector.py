from datetime import datetime, timedelta
import numpy as np
import time

class TimeSelector:

    def __init__(self, ncf):
        self.ncf = ncf


        dt0 = datetime(2015,3,1,0,0) # start time for decimal hours
        ts0 = time.mktime(dt0.timetuple()) # start unix timestamp for decimal hours 
        self.dt = [datetime.fromtimestamp(t) for t in ncf['time'][:]] # datetimes 
        self.decHrs = (ncf['time'][:] - ts0)/3600 # decimal hours since start time
        self.fullHrs = np.floor(self.decHrs).astype(np.int) # full hour values
        #self.uniqHrs = np.unique(self.fullHrs) # only unique full hour values
        self.decDays = (ncf['time'][:] - ts0)/86400 # decimal days since start time
        self.fullDays = np.floor(self.decDays).astype(np.int) # full day values
        #self.uniqDays = np.unique(self.fullDays) # only unique full day values

        self.years = np.asarray([t.year for t in self.dt])
        self.months = np.asarray([t.month for t in self.dt])
        self.days = np.asarray([t.day for t in self.dt])
        self.hours = np.asarray([t.hour for t in self.dt])
        self.minutes = np.asarray([t.minute for t in self.dt])

        #i0 = 3700
        #i1 = 4300
        #i0 = 87650
        #i1 = i0+100
        #for i in range(i0,i1):
        #    print(self.dt[i])

        # Mask containing 0 or 1 depending if the values should be selected
        self.sel = {} 
        # Array containing the indices of the values that should be selected
        self.selInds = {}

        ## Array contatining the indices for the datetimes of the structured output
        #self.sdti = None


    def selTime(self, selKey, year=None, month=None, day=None, hour=None, minute=None, reset=True):
        """Alters mask self.sel according to user time input. Creates"""
        # reset means that the current selection should be overwritten
        if reset:
            s = np.ones(len(self.dt), dtype=np.int8)
        else:
            if selKey not in self.sel:
                raise ValueError('selection Key ' + selKey + ' does not yet exist.')
            else:
                s = self.sel[selKey]

        if year != None:
            s[self.years != year] = 0
        if month != None:
            s[self.months != month] = 0
        if day != None:
            s[self.days != day] = 0
        if hour != None:
            s[self.hours != hour] = 0
        if minute != None:
            s[self.minutes != minute] = 0
        sI = np.nonzero(s)[0]
        self.sel[selKey] = s
        self.selInds[selKey] = sI

    def getStructuredDatsetimes(self):
        datet = np.asarray(self.dt)
        return(datet[self.sdti])



    def getVar(self, varName, selKey, structure=None):
        # output value array
        out = None
        
        #self.sdti = []
        if selKey not in self.selInds:
            raise ValueError('selection Key ' + selKey + ' does not exist.')

        if len(self.selInds[selKey]) > 0:
            # STRUCTURE OUTPUT AS 2D ARRAY (row: days, cols: timesteps of each day)
            if structure == 'day':
                vals = self.ncf[varName][self.selInds[selKey]]
                seldts = list(self.dt[i] for i in self.selInds[selKey])

                indices = np.zeros(np.ceil(len(seldts)/144).astype(np.int),np.int)
                j = 0
                for i,dt in enumerate(seldts):
                    if (dt.minute == 0) & (dt.hour == 0):
                        indices[j] = i
                        j = j + 1
                out_vals = np.zeros((len(indices),144))
                out_dt = []
                for i,ind in enumerate(indices):
                    out_vals[i,:] = vals[ind:(ind+144)]
                    out_dt.append(seldts[ind])

            # STRUCTURE OUTPUT AS 2D ARRAY (row: hours, cols: timesteps of each hour)
            elif structure == 'hour':
                vals = self.ncf[varName][self.selInds[selKey]]
                seldts = list(self.dt[i] for i in self.selInds[selKey])

                indices = np.zeros(np.ceil(len(seldts)/6).astype(np.int),np.int)
                j = 0
                for i,dt in enumerate(seldts):
                    if dt.minute == 0:
                        indices[j] = i
                        j = j + 1
                out_vals = np.zeros((len(indices),6))
                out_dt = []
                for i,ind in enumerate(indices):
                    out_vals[i,:] = vals[ind:(ind+6)]
                    out_dt.append(seldts[ind])

            elif structure == 'minute':
                out_vals = self.ncf[varName][self.selInds[selKey]]
                seldts = list(self.dt[i] for i in self.selInds[selKey])
                out_dt = seldts
            else:
                raise ValueError('invalide structure argument')

        return(out_vals, out_dt)


    def getDayValInd(self, hour, min):
        return(int(min/10 + hour*6))

    def getHourValInd(self, min):
        return(int(min/10))
