import random
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm, gamma
from calendar import monthrange

""" 
Class Consumer with static attributes
- consumerID
- Age
- Income
- Device 
- Gender

and dynamic attributes
- mailing_frequency
- timespan
- product_purchase 
- prior_email_opening

and behavior
- informative_perception

and counters.
"""
class Consumer:
        def __init__(self, consumerID, age, income):
                """ 
                Initilizes the class with creation of static and dynamic 
                attributes and consumer behavior.

                Args
                -------
                consumerID:             Unique ID of Consumer object
                age:                    Defined age according to defined distribution and correlation.
                income:                 Defined income according to defined distribution and correlation.
                device:                 Defined device which consumer uses most frequently.

                Returns
                -------
                None 

                """
                # Static attributes
                self.gender = self.generate_gender()
                self.consumerID = consumerID
                self.age = age
                self.income = income
                device = self.generate_device()
                self.device = device[0]
                self.device_influence = device[1]
                # Dynamic attributes
                self.mailing_frequency = 0
                self.timespan = 0
                self.product_purchase = False
                self.prior_email_opening = False
                # Behavior
                self.informative_perception = self.generate_informative_perception()
                # Counters
                self.mailing_counter = 0
                self.mailing_timestamps = []
                self.last_mailing = 0
                self.purchase_date = None
        
        def generate_gender(self):
                """ 
                Generates gender of consumer. 

                Args
                -------
                consumer_amount:                Amount of consumers for desired size of age sample. 

                Returns
                -------
                age_sample:                     Age sample of desired size. 

                """
                gender_categories = ["Männlich", "Weiblich"]
                gender_probabilities = [0.59, 0.41]
                gender = np.random.choice(gender_categories, p=gender_probabilities)
                return gender
        
        def generate_device(self):
                """ 
                Defines device that consumer uses to open email messages. 
                
                Args
                -------
                None

                Returns
                -------
                device: Device of consumer.  
                device_influence: Regression coefficient of device with direct influence on OR.

                """
                device_categories = ["Mobil", "Desktop"]
                device = "Desktop"
                if self.age <= 19:
                        device_probabilities = [0.942, 0.058]
                elif 20 <= self.age <= 29:
                        device_probabilities = [0.955, 0.045]
                elif 30 <= self.age <= 39:
                        device_probabilities = [0.96, 0.04]
                elif 40 <= self.age <= 49:
                        device_probabilities = [0.957, 0.043]
                elif 50 <= self.age <= 59:
                        device_probabilities = [0.928, 0.072]
                elif 60 <= self.age <= 69:
                        device_probabilities = [0.852, 0.148]
                elif self.age >= 70:
                        device_probabilities = [0.682, 0.318]
                else:
                        print("No device")

                device = np.random.choice(device_categories, p=device_probabilities)

                device_influence = 0
                if device == "Mobil":
                        device_influence = 0.9
                if device == "Desktop":
                        device_influence = 0

                return device, device_influence
        
        def generate_informative_perception(self):
                """ 
                Defines informative_perception of consumer in the simulation.
                Static attributes taken into consideration are age, gender and income.

                Args
                -------
                self

                Returns
                -------
                informative_perception: Informative perception of individual consumer
                                        based on static atttributes age, gender and income
                                        which defines behavior of consumer in simulation. 

                """
                informative_perception = 0
                age_perception = 0
                gender_perception = 0
                income_perception = 0

                if self.age < 44:
                        age_perception = 0
                elif self.age > 44 or self.age <54:
                        age_perception = -1.2
                elif self.age >= 55:
                        age_perception = -1.1

                if self.gender == "Männlich":
                        gender_perception = 0.3
                elif self.gender == "Weiblich":
                        gender_perception = 0

                if self.income < 3792:
                        income_perception = 0
                elif self.income in range(3792,7583):
                        income_perception = 0.4
                elif self.income in range(7584,15167):
                        income_perception = -0.1
                elif self.income > 15167:
                        income_perception = -0.1   
                informative_perception = age_perception + gender_perception + income_perception
                return informative_perception

        def create_consumers(consumer_amount):
                """ 
                Creates consumer sample based on defined consumer_amount.
                First correlated static attributes are generated. 
                Afterwards consumers are created with non-correlated static attributes
                and dynamic attributes. Consumers are appended to consumers list. 
                
                Args
                -------
                consumer_amount: Amount of consumers in simulation defined by user.

                Returns
                -------
                consumers:      List of consumers with defined attributes, behavior and 
                                statistical measures. 

                """
                consumers = []
                
                # Create correlated samples of age and income 
                correlated_age_income = generate_correlated_age_income(consumer_amount)
                age_sample = np.round(correlated_age_income[0])
                income_sample = np.round(correlated_age_income[1])

                for i in range(0, consumer_amount):
                        consumer = Consumer(i+1, int(age_sample[i]), int(income_sample[i]))
                        consumers.append(consumer)
                return consumers
                
        def create_purchase_list(simulation_time_days, buying_frequency_per_month, share_buyers, consumers, timestep_size):
                """ 
                Creates purchase list based on input parameters for whole simulation time.
                Purchase list contains dates and Consumer objects as buyers for each date.
                
                Args
                -------
                simulation_time_days:           Counter  for simulation days
                buying_frequency_per_month:     Specified buying frequency per month.
                share_buyers:                   Share of consumers who buy products.
                consumers:                      List of consumers in simulation.
                timestep_size:                  Specified time step size.

                Returns
                -------
                purchase_list:                  List of buyers with defined purchase dates.

                """
                purchase_list = []
                current_time = datetime.now() - timedelta(days=simulation_time_days)
                end_time = datetime.now()
                num_buyers = round(len(consumers) * share_buyers)
                buyers = random.sample(consumers, num_buyers)

                buyers_per_month = {k: round(num_buyers * v) for k, v in buying_frequency_per_month.items()}

                purchases_made = 0
                while current_time < end_time:
                        month = current_time.strftime("%Y-%m")
                        year = current_time.year
                        days_in_month = monthrange(year, int(month.split("-")[1]))[1]
                        
                        # This will get the number of purchases needed for the entire month
                        total_purchases_for_month = buyers_per_month[month.split("-")[1]]
                        
                        # Calculate purchases for the current day based on remaining monthly purchases and remaining days
                        purchases_per_day = round(total_purchases_for_month / (days_in_month - current_time.day + 1))
                        purchases_per_day = min(purchases_per_day, total_purchases_for_month)  # Ensure not to exceed total monthly purchases
                        
                        # Deduct the purchases of the current day from the total monthly purchases
                        buyers_per_month[month.split("-")[1]] -= purchases_per_day

                        for _ in range(purchases_per_day):
                                if purchases_made < num_buyers:
                                        buyer = buyers[purchases_made]
                                        purchase_list.append((buyer, current_time))
                                        purchases_made += 1

                        current_time += timedelta(days=timestep_size)

                purchase_list.sort(key=lambda x: x[1])
                return purchase_list
        
        def calculate_frequency(dispatch_timestamps, current_time):
                """ 
                Calculates mailing frequency of last 30 days of consumer at time of email dispatch.

                Args
                -------
                dispatch_timestamps:            Consumers list of dispatch timestamps.
                current_time:                   Current time in simulation.

                Returns
                -------
                frequency:                      Amount of emails in last 30 days of consumer.

                """
                days_cutoff = current_time - timedelta(days=30)
                frequency = sum(1 for timestamp in dispatch_timestamps if timestamp >= days_cutoff)
                return frequency

        def calculate_timespan(dispatch_timestamps, current_time):
                """ 
                Calculates timespan since last email dispatch to consumer.

                Args
                -------
                dispatch_timestamps:            Consumers list of dispatch timestamps.
                current_time:                   Current time in simulation.

                Returns
                -------
                timespan:                       Amount of days since last dispatch to consumer.

                """
                if len(dispatch_timestamps) != 0:
                        difference = current_time - dispatch_timestamps[-1]
                        timespan = difference.days
                elif len(dispatch_timestamps) == 0:
                        timespan = 0
                return timespan
        
def create_custom_distribution_gamma(mean, std_dev, range_min, size):
        """ 
        Creates amount of size of custom gamma distribution with defined mean, standard deviation and range minmum.

        Args
        -------
        mean:                           Desired mean of distribution.
        std_dev:                        Desired standard deviation of distribution.
        range_min:                      Desired range minimum of distribution.
        size:                           Desired amount of samples.

        Returns
        -------
        samples:                        Samples with the desired gamma distribution.

        """
        samples = []
        variance = std_dev ** 2
        shape = (mean**2) / variance
        scale = variance / mean
        while len(samples) < size:
                sample_distribution = gamma.rvs(a=shape, scale=scale, size=size-len(samples))
                for sample in sample_distribution:
                        if sample >= range_min:
                                samples.append(sample)
                        if len(samples) == size:
                                break
        return samples

def generate_age(consumer_amount):
        """ 
        Generates age samples based on consumer amount. 
        Method not used in current implementation but kept in for research purposes.

        Args
        -------
        consumer_amount:                Amount of consumers for desired size of age sample. 

        Returns
        -------
        age_sample:                     Age sample of desired size. 

        """
        age_mean = 40.53
        age_mode = 39.5
        age_std = 10.94
        age_min = 18
        age_max = 80
        age_variance = 119.7841
        age_skewness = 0.04956
        #alter_skewness = 0
        age_kurtosis = -1.3
        #alter_kurtosis = 3
        age_sample = create_custom_distribution_gamma(age_mean, age_std, age_min, consumer_amount)
        #age_sample = truncated_skew_normal_kurt(age_mean, age_std, age_min, age_max, age_skewness, age_kurtosis, consumer_amount)
        return age_sample
                
def generate_correlated_age_income(consumer_amount):
        """ 
        Generates correlated age and income samples based on consumer amount. 

        Args
        -------
        consumer_amount:                Amount of consumers for desired size of age sample. 

        Returns
        -------
        age_sample:                     Correlated age sample of desired size. 
        income_sample:                  Correlated income sample of desired size. 

        """
        size = consumer_amount
        correlation_age_income = 0.46

        income_min = 2083
        income_mean = 9688 - income_min
        income_std = 5459
        income_variance = income_std**2
        shape_income = (income_mean**2) / income_variance
        scale_income = income_variance / income_mean

        age_min = 18
        age_mean = 40.5 - age_min
        age_std = 10.9
        age_variance = age_std**2
        shape_age = (age_mean**2) / age_variance
        scale_age = age_variance / age_mean

        X = np.random.normal(0, 1, size)
        Y = correlation_age_income * X + np.sqrt(1 - correlation_age_income**2) * np.random.normal(0, 1, size)

        income_sample = gamma.ppf(norm.cdf(X), a=shape_income, scale=scale_income) + income_min
        age_sample = gamma.ppf(norm.cdf(Y), a=shape_age, scale=scale_age) + age_min

        return age_sample, income_sample