# Tip Assistant program
# Uses textfiles containing till and hours worked to calculate tip distribution
# Since tip money is usually small denominations, calculates what coins to exchange 
# for larger denominations as appropriate.

# Assumptions:
# - All Canadian currency: lowest denomination is nickels, highest twenties
# - Denominations can be broken down arbitrarily into smaller bills or coins
# - Rolls of 40 quarters, 50 dimes, or 20 nickels, can be exchanged for two fives,
#   one five, or loonies, respectively.

import datetime as dt

# Money file should contain eight integers only, each separated by \n
# Integers represent number of twenties, tens, fives, toonies, loonies, quarters, 
# dimes, and nickels that one starts with.

moneyfile = "money.txt"

# Roster file is more complicated. 
# First line should contain period start date in yyyy/mm/dd format
# Second line should contain period end date in same format.
# Third, fifth, etc. lines should contain employee names.
# Fourth, sixth, etc. lines should contain hours each respective employee worked.

rosterfile = "roster.txt"

# Helper function. Take float and returns string in proper currency format: "xxx.xx CAD".

def curr_format(money):
    sm = str(round(money,2))
    if sm[-3] == ".":
        sm = sm + " CAD"
    elif sm[-2] == ".":
        sm = sm + "0 CAD"
    else:
        sm = sm + ".00 CAD"
    return(sm)


# Define till class
 
class Till:
    
    # Initiated to be empty.
    # moneyfile may be None if the object is not initiated from a text file.
    
    def __init__(self,moneyfile):
        self.denom = [20,10,5,2,1,.25,.1,.05]
        self.till = dict()
        for k in self.denom:
            self.till[str(k)] =  0
        self.mfn = moneyfile            
    
    # Return total value of till.
    
    def haul(self):
        return(round(sum([k*self.till[str(k)] for k in self.denom]),2))

    # Exchange n bills/coins of one denomination (p1) into another (p2)
    
    def change(self,p1,p2,n):
        if p1 in self.denom and p2 in self.denom:
            if p1 > p2:
                
                # Odd numbers of fives or quarters cannot be changed into toonies
                # and dimes, respectively. 
            
                if n % 2 ==1 and (p1 == 5 and p2 == 2) or (p1 == .25 and p2 == .10):
                    print("Exchange error")

                # n must not exceed what's in the till
                
                elif n > self.till[str(p1)]:
                    print("Exchange error")
                else:
                    self.till[str(p1)] -= n
                    self.till[str(p2)] += int(n*p1/p2)
            elif p1 < p2:
                
                # When exchanging smaller for larger, n must be a certain multiple
                if n*p1 % p2 != 0:
                    print("Exchange error")
                else:
                    self.till[str(p1)] -= n
                    self.till[str(p2)] += int(n*p1/p2)

    # Compare two tills. Returns the differences in each denomination
            
    def compare(self,till2):
        delta = dict()
        for k in self.denom:
            delta[str(k)] = self.till[str(k)] - till2.till[str(k)]
        return(delta)
    
    # Read data from text file
    
    def read(self):
        
        with open(self.mfn) as f:
            self.till['20'] = int(f.readline())
            self.till['10'] = int(f.readline())
            self.till['5'] = int(f.readline())
            self.till['2'] = int(f.readline())
            self.till['1'] = int(f.readline())
            self.till['0.25'] = int(f.readline())
            self.till['0.1'] = int(f.readline())
            self.till['0.05'] = int(f.readline())

    # Given a till and an hours report, breaks down denominations so that the tip
    # shares can be paid.

    def refine(self,hours):

        # Copy tips locally
        tips = dict()
        for k in hours.tips.keys():
            tips[k] = hours.tips[k]

        # Break down each denomination
        for k in self.denom[0:7]:
            
            # Running total of bills/coins remaining
            rt = self.till[str(k)]
            
            # Apportion bills to each person as needed
            for g in hours.roster.keys():
                portion = min(rt, int(tips[g]/k))
                rt -= portion
                tips[g] = round(tips[g] - portion*k,2)
                if rt==0:
                    break
                
            # Exchange remaining bills/coins for smaller
            self.till[str(k)] -= rt
            if rt > 0:
                # For fives, exchange for loonies (not toonies)
                if k == 5:
                    self.till['1'] += 5*rt
                # For quarters, okay to exchange for dimes (plus a nickel if needed)
                elif k == 0.25:
                    self.till['0.1'] += int(2.5*rt)
                    self.till['0.05'] += rt % 2
                else:
                    nxt = self.denom[self.denom.index(k) + 1]
                    self.till[str(nxt)] += int(k/nxt)*rt
    
    # Lots of nickels/dimes/quarters are undesirable, so this method cleans that up.
    # This method should not be applied unless till has already been refined!
                 
    def coarsen(self,hours):
        
        # Compute absolutely essential nickels/dimes/quarters
        essq, essd, essn = 0, 0, 0
        for g in hours.roster.keys():
            essq += int( round(hours.tips[g] % 1,2)*4)
            essd +=  int((round(hours.tips[g] % .25,2))*10)
            essn += round(round(round(hours.tips[g] % .25, 2) % .1,2)*20)
        
        # Afer subtracting essentials, compute number of rolls that can be exchanged
        # 40 quarters per roll, 50 dimes, 20 nickels
        qrolls = int((self.till['0.25'] - essq)/40)
        drolls = int((self.till['0.1'] - essd)/50)
        nrolls = int((self.till['0.05'] - essn)/20)

        # Alter till to reflect exchange
        self.till['0.25'] -= qrolls*40
        self.till['0.1'] -= drolls*50
        self.till['0.05'] -= nrolls*20
        self.till['5'] += 2*qrolls + drolls
        self.till['1'] += nrolls

# Hours class contains a dict containing the hours worked for each employee for the given timeframe
# Also contains start and end dates
# Requires a till input so that tips can be computed

class Hours:
    
    def __init__(self, till, rosterfile):
        
        # Upon initiation, the rosterfile (see above for format) is used to populate the dict
        # Unlike the Till class, the filename here cannot be None
        with open(rosterfile) as f:

            # Start and end dates read first
            l = [int(d) for d in f.readline().split("/")]
            self.start = dt.date(l[0],l[1],l[2])
            l2 = [int(d) for d in f.readline().split("/")]
            self.end = dt.date(l2[0],l2[1],l2[2])
            self.roster = dict()
            
            # As long as there are lines to read, populate the dict
            self.distro = dict()
            while True:
                name = f.readline()
                if len(name) <=1:
                    break
                else:
                    name = name[0:(len(name)-1)]
                    hours = round(float(f.readline()),2)
                    self.roster[name] = hours
                    self.distro[name] = [0,0,0,0,0,0,0,0,0]

        # Tips not computed on initiation 
        self.tips = dict()
               
        for k in self.roster:
            self.tips[k] = 0
        
        # Compute tip total
        self.total = till.haul()
        

    # Return total hours worked
    def total_hours(self):
        return(sum([x for x in self.roster.values()]))

    # Compute percentage share that each employee is owed
    def fraction(self):
        return(self.total/self.total_hours())

    # Compute tips
    def tips_compute(self):

        # First compute unrounded tips
        rawtips = dict()
        for k in self.roster.keys():
            rawtips[k] = self.roster[k]*self.fraction()
            
        # Now round            
        for k in self.tips.keys():
            self.tips[k] = round(20*rawtips[k])/20
        
        # Rounding might throw off tip total.Typically just a matter of a few nickels,
        # but still this should be dealth with fairly. Any extra nickels should be
        # given to the folks who were hurt most by rounding. And, any absent nickels
        # should be subtracted from those who most benefited.
        
        if sum(self.tips.values()) != self.total:
            discrep = round((sum(self.tips.values()) - self.total)*20)
            detail = dict()

            # Compute the rounding errors 
            for g in self.roster.keys(): 
                detail[g] = rawtips[g] - self.tips[g]
                
            # If there are extra nickels
            if sum(self.tips.values()) < self.total:
                thresh = sorted(detail.values(),reverse=True)[-discrep]
                for g in self.roster.keys():
                    if detail[g] > thresh:
                        self.tips[g] += .05
                        
            # If there are not enough nickels
            else:
                thresh = sorted(detail.values())[discrep]
                for g in self.roster.keys():
                    if detail[g] < thresh:
                        self.tips[g] -= .05 
            
    
    # Compute how the actual bills and coins should be distributed

    def distribute(self,till):        
        
        # Start at largest denomination and work down
        for k in till.denom[0:8]:
            loot = till.till[str(k)]
            
            # Try and distribute evenly (e.g. don't give out the most fives to the first person,
            # rather, try to make sure everyone gets a five).
            while loot > 0:
                for g in self.roster.keys():
                    if loot == 0:
                        pass
                    elif round(self.tips[g] - self.distro[g][8],2) >= k:
                        self.distro[g][till.denom.index(k)] += 1
                        self.distro[g][8] = round(self.distro[g][8] + k,2)
                        loot -= 1


# This class is a composite class, containing the hours and two tills: the original,
# as well as the refined/coarsened till.

class TipReport:
    
    # Initiate by reading the original till, and hours. 
    def __init__(self,today):
        self.date = today
        self.ot = Till("money.txt")
        self.ot.read()
        self.tw = Hours(self.ot,rosterfile)
        
        # Compute tips
        self.tw.tips_compute()
        
        # Create destination till by refining and coarsening
        self.nt = Till(None)
        for k in self.nt.till.keys():
            self.nt.till[k] = self.ot.till[k]
        self.nt.refine(self.tw) 
        self.nt.coarsen(self.tw)
        
        # Compute distribution
        self.tw.distribute(self.nt)

    # The original version ended up giving out too many quarters and dimes to the higher earner.
    # This was an artifact of coin rolls being too big. This method is added to correct that.
    # The unfortunate side-effect is that coin exchange becomes a pain on the physical end.
    # C'est la vie.
    def distro_correct(self):

        for g in self.tw.roster.keys():

            # Exchange excess nickels        
            if self.tw.distro[g][7] > 1:
                newd = int(self.tw.distro[g][7]/2)
                self.nt.till['0.1'] += newd
                self.nt.till['0.05'] -= newd*2
                self.tw.distro[g][6] += newd
                self.tw.distro[g][7] -= newd*2
            # Exchange excess dimes        
            if self.tw.distro[g][6] > 4:
                newq = int(self.tw.distro[g][6]/5)
                self.nt.till['0.25'] += newq*2
                self.nt.till['0.1'] -= newq*5
                self.tw.distro[g][5] += newq*2
                self.tw.distro[g][6] -= newq*5
            # Exchange excess quarters        
            if self.tw.distro[g][5] > 3:
                newl = int(self.tw.distro[g][5]/4)
                self.nt.till['1'] += newl
                self.nt.till['0.25'] -= newl*4
                self.tw.distro[g][4] += newl
                self.tw.distro[g][5] -= newl*4


    # Create report string
    def format(self):
        
        # Header contains dates, as well as total hours and total tips
        report = "TIP REPORT\n"
        report +="----------\n\n"
        report += "Report date: "  + str(self.date.year) + " / " + str(self.date.month) + " / " + str(self.date.day)  +"\n"
        report += "Period start date: "  + str(self.tw.start.year) + " / " + str(self.tw.start.month) + " / " + str(self.tw.start.day) +"\n"
        report += "Period end date: "  + str(self.tw.end.year) + " / " + str(self.tw.end.month) + " / " + str(self.tw.end.day) +"\n"
        
        report += "\n" + "Total hours: " + str(round(self.tw.total_hours(),2))
        report += "\n" + "Total tips: " + curr_format(self.tw.total) + "\n\n"
        
        # For each employee, print tips earned, as well as how much of each bill/coin
        # they get.
        for g in self.tw.roster.keys():
            report += g + " gets " + curr_format(self.tw.tips[g]) + " in tips. \n"
            denom = ["Twenties: ", "Tens: ", "Fives: ", "Toonies: ", "Loonies: ", "Quarters: ", "Dimes: ", "Nickels: "]
            for l in range(0,8): 
                k = self.tw.distro[g][l]
                if k == 0:
                    pass
                else:
                    report += denom[l] + str(k) +"\n"
            report += "\n"
            
        # Finally, report how many of each denomination needs to be exchanged or obtained
        # in order to accomplish the refine/coarsening operations.
        if self.ot.till['20'] != self.nt.till['20']:
            report += "Number of twenties to break: " + str(self.ot.till['20'] - self.nt.till['20']) + '\n'

        if self.ot.till['10'] > self.nt.till['10']:
            report += "Number of tens to break: " + str(self.ot.till['10'] - self.nt.till['10']) + '\n'
        elif self.ot.till['10'] < self.nt.till['10']:
            report += "Number of tens to obtain: " + str(self.nt.till['10'] - self.ot.till['10']) + '\n'

        if self.ot.till['5'] > self.nt.till['5']:
            report += "Number of fives to break: " + str(self.ot.till['5'] - self.nt.till['5']) + '\n'
        elif self.ot.till['5'] < self.nt.till['5']:
            report += "Number of fives to obtain: " + str(self.nt.till['5'] - self.ot.till['5']) + '\n'

        if self.ot.till['2'] != self.nt.till['2']:
            report += "Number of toonies to break: " + str(self.ot.till['2'] - self.nt.till['2']) + '\n'

        if self.ot.till['1'] > self.nt.till['1']:
            report += "Number of loonies to break: " + str(self.ot.till['1'] - self.nt.till['1']) + '\n'
        elif self.ot.till['1'] < self.nt.till['1']:
            report += "Number of loonies to obtain: " + str(self.nt.till['1'] - self.ot.till['1']) + '\n'

        if self.ot.till['0.25'] > self.nt.till['0.25']:
            report += "Number of quarters to exchange: " + str(self.ot.till['0.25'] - self.nt.till['0.25']) + '\n'
        elif self.ot.till['0.25'] < self.nt.till['0.25']:
            report += "Number of quarters to obtain: " + str(self.nt.till['0.25'] - self.ot.till['0.25']) + '\n'

        if self.ot.till['0.1'] > self.nt.till['0.1']:
            report += "Number of dimes to exchange: " + str(self.ot.till['0.1'] - self.nt.till['0.1']) + '\n'
        elif self.ot.till['0.1'] < self.nt.till['0.1']:
            report += "Number of dimes to obtain: " + str(self.nt.till['0.1'] - self.ot.till['0.1']) + '\n'

        if self.ot.till['0.05'] > self.nt.till['0.05']:
            report += "Number of nickels to exchange: " + str(self.ot.till['0.05'] - self.nt.till['0.05']) + '\n'
        elif self.ot.till['0.05'] < self.nt.till['0.05']:
            report += "Number of nickels to obtain: " + str(self.nt.till['0.05'] - self.ot.till['0.05']) + '\n'

        return(report)
        
        
# Create report
tr = TipReport(dt.date.today())
tr.distro_correct()
report = tr.format()

# Print to screen
print("\n")
print(report)

# Save in file. Filename is Report plus the three dates.
fname = "Report_" + str(tr.date)+ "_" + str(tr.tw.start) + "_" + str(tr.tw.end) + ".txt"
fname = fname.replace("-","")
with open(fname,"w+") as f:
    f.write(report)
