# Simulates the gambling game of Lecture # 1
#
# MS&E 223: Simulation
#
# Usage: python gamble.py -n k [-t -i -d m]
# where -n (--num) k: Number of replications given by k
# -t (--trial): Trial run to get required number of replications
# -i (--confint): Calculate the CI of the point estimator
# -d (--debug) m: Verbose output needed, levels from 0-2
#
# Uses the clcg4 module (the module should be in the python path or the same folder)
__author__ = "Sharan Srinivasan"

from rng import clcg4
from math import sqrt
from argparse import ArgumentParser

class Estimator:
    """ Computes point estimates and confidence intervals """
    def __init__(self, z, conf_str):
        self.k = 0  # number of values processed so far
        self.sum = 0.0  # running sum of values
        self.v = 0.0  # running value of (k-1)*Variance
        self.z = float(z) # quantile for normal Confidence Interval
        self.conf_str = conf_str # string of form "xx%" for xx% Confidence Interval

    def reset(self):
        self.k = 0
        self.sum = 0
        self.v = 0

    def process_next_val(self, value):
        self.k += 1
        if self.k > 1:
            diff = self.sum - (self.k - 1) * value
            self.v += diff/self.k * diff/(self.k-1)
        self.sum += value

    def get_variance(self):
        if self.k > 1:
            var = self.v/(self.k-1)
        else:
            raise RuntimeError("Variance undefined for number of observations = 1")
        return var

    def get_mean(self):
        return self.sum/self.k if self.k > 1 else 0

    def get_conf_interval(self):
        hw = self.z * sqrt(self.get_variance()/self.k)
        point_est = self.get_mean()
        c_low = point_est - hw
        c_high = point_est + hw
        return self.conf_str + " Confidence Interval [ %.4f" %c_low +  ", %.4f" %c_high + "]"

    def get_num_trials(self, epsilon, relative=True):
        var = self.get_variance()
        width = self.get_mean() * epsilon if relative else epsilon
        return int((var * self.z * self.z)/(width * width))

def do_rep(unigen, est):
    """ Returns the amount of money earned during a single replication """
    num_heads = 0
    num_tails = 0
    diff = 0
    while abs(diff) < 3:
        if unigen.next_value(1) <= 0.5:
            num_heads += 1
            verbose_print(2, "H ")
        else:
            num_tails += 1
            verbose_print(2, "T ")
        diff = num_heads - num_tails
    verbose_print(2, "\n")
    val = 8.99 - (num_heads + num_tails)
    est.process_next_val(val)
    return val

if __name__ == "__main__":
    # parse command line arguments
    parser = ArgumentParser(description = "gamble -n [--trial --confint --debug m]")
    parser.add_argument('-n', '--num', help="Number of replications", required=True)
    parser.add_argument('-t', '--trial', help="Trial run to get required number of replications", action='store_true')
    parser.add_argument('-i', '--confint', help="Calculate the CI of the point estimator", action='store_true')
    parser.add_argument('-d', '--debug', help="Verbose output needed", default=0)
    sysargs = parser.parse_args()

    est = Estimator(1.96, "95%")  # 95% CI
    epsilon = 0.005  # Determines the width of the CI
    unigen = clcg4.Clcg4()  # Instantiate the random number generator
    unigen.init_default()

    # verbose printing for different debug levels
    def verbose_print(level, *args):
        if level <= int(sysargs.debug):
            for arg in args:
                print arg,
        else:
            pass
            
    # reinitialize generator for production runs
    if not sysargs.trial: unigen.init_generator(1, clcg4.NEW_SEED)

    # run simulation repetitions and collect stats
    for rep in range(int(sysargs.num)):
        val = do_rep(unigen, est)
        verbose_print(1, "Repetition", rep+1, " : %.2f" %val, "\n\n")

    # print results
    verbose_print(0, "Average net gain: %.3f" %est.get_mean())
    if sysargs.confint:
        verbose_print(0, "with", est.get_conf_interval())
    print "\n"
    if sysargs.trial:
        print "Est. # of repetitions for +/-", epsilon, "accuracy: ", est.get_num_trials(epsilon, False)
    
        
        

        
