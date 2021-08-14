import pandas as pd 
import eeprivacy
from eeprivacy.mechanisms import *
from eeprivacy.operations import *

class PrivateVector:
    def __init__(self, values, lower_bound, upper_bound, confidence=0.95):
        self.n = len(values)
        self.k = len(values[0])
        self.values = values
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound 
        self.confidence = confidence
        self.gaussian = PrivateVectorClampedMeanGaussian(lower_bound=lower_bound, upper_bound=upper_bound, k=self.k, N=self.n)

    def actual_means(self):
        return np.mean(self.values, 0)

    def private_means(self, epsilon):
        return self.gaussian.execute(vectors=self.values, epsilon=epsilon, delta=1/(self.n**2))

    def private_ci(self, epsilon):
        return self.gaussian.confidence_interval(epsilon=epsilon, delta=1/(self.n**2), confidence=self.confidence)

    def private_sensitivity(self):
        return self.gaussian.sensitivity

    def epsilon_for_confidence_interval(self, target_ci, delta=None, confidence=0.95):
        if delta is None:
            delta = 1/(self.n**2)
        return self.gaussian.epsilon_for_confidence_interval(target_ci=target_ci, delta=delta, confidence=confidence)

    
    def private_trials(self, epsilon, n=100000):
        trials = [] 
        means = self.private_means()
        for i in range(n):
          # compute monte carlo simulation, for use later on
          trials.append(GaussianMechanism.execute_batch(
            values=means, 
            epsilon=epsilon,
            delta=1/(self.n**2),
            sensitivity=self.private_sensitivity()
        ))
        return trials
      

class PrivateLoadShape(PrivateVector):
    def __init__(self, df, index_column, time_column, value_column, quantile_cutoff_lower=0.02, quantile_cutoff_upper=0.98, confidence=0.95):
        self.lower_bound = df[value_column].quantile(quantile_cutoff_lower)
        self.upper_bound = df[value_column].quantile(quantile_cutoff_upper)
        df = df[df[value_column] >= self.lower_bound]
        df = df[df[value_column] <= self.upper_bound]
        self.df = df
        self.time_index = df[time_column].drop_duplicates()
        self.index_column = index_column
        self.value_column = value_column
        self.time_column = time_column
        self.df_wide = self.df.pivot(index=self.index_column, columns=self.time_column, values=self.value_column).dropna().to_numpy()
        self.n = len(self.df_wide)
        super().__init__(values=self.df_wide, lower_bound=self.lower_bound, upper_bound=self.upper_bound, confidence=confidence)
                

    def mean_usage(self):
        return self.df[self.value_column].mean()  


    # def noise_epsilon_mapping(self):
    #     mean = self.mean_usage()
    #     epsilons = np.logspace(-0.5, 2.3, 200)
    #     noises = [self.estimate_noise(e) / self.mean_usage() for e in epsilons]
    #     return pd.DataFrame({'noise_pct': noises, 'epsilon': epsilons})

    # def estimate_epsilon(self, noise_pct):
    #     df = self.noise_epsilon_mapping()
    #     if (noise_pct < df.noise_pct.min()) | (noise_pct > df.noise_pct.max()):
    #         return None 
    #     else:
    #         return df[df.noise_pct >= noise_pct].sort_values('noise_pct', ascending=True)['epsilon'].iloc[0]
            

    def privatize(self, epsilon):        
        means = self.private_means(epsilon)
        return pd.DataFrame({
            self.time_column: self.time_index,            
            'private_ci': self.private_ci(epsilon),
            'private_mean': means,
            'private_max': means + self.private_ci(epsilon),
            'private_min': means - self.private_ci(epsilon),
            'actual_mean': self.actual_means(),
            'noise_added_pct':  (abs(self.private_ci(epsilon))) / self.actual_means()
            }).sort_values(self.time_column)


