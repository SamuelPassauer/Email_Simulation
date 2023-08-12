import numpy as np
from datetime import datetime, timedelta
from scipy.stats import skewnorm

""" 
E-Mail with attributes
- emailID
- length
- sending_day
- sending_day_influence
- personalization

For all attributes, possible values with probabilities of 
occurrence are defined and in this way an individual consumer is generated. 
"""
class Email_Object:
        def __init__(self, emailID):  
                """ 
                Initilizes the class with creation of email attributes.

                Args
                -------
                emailID:                Unique ID of Email_Object object.

                Returns
                -------
                None 

                """
                self.emailID = emailID
                length = self.generate_length()
                self.length = length[0]
                self.information_value = length[1]
                sending_day = self.generate_sending_day()
                self.sending_day = sending_day[0]
                self.sending_day_influence = sending_day[1]
                self.personalization = "Keine Personalisierung"

        def generate_length(self):
                """ 
                Generates distribution of length and informative value of subject line .

                Args
                -------
                None.

                Returns
                -------
                length:                 Subject line length.             
                information_value:      Informative value of subject line.

                """
                information_value = 0
                subject_line_mean = 7.9
                subject_line_std = 2.3
                subject_line_min = 0
                subject_line_max = np.inf
                subject_line_skewness = -0.5
                length = np.round(self.create_custom_distribution_norm(subject_line_mean, subject_line_std, subject_line_skewness, subject_line_min, subject_line_max, size=1))[0]

                if length > 7:
                        information_value = 1
                elif length <= 7:
                        information_value = -1
                return length, information_value
        
        def generate_sending_day(self):
                """ 
                Generates sending day of Email_Object and corresponding influence value as regression coefficient.

                Args
                -------
                None.

                Returns
                -------
                sending_day:            Chosen sending day out of sending day categories. 
                sending_day_influence:  Defined  sending day influence.

                """
                sending_day_influence = 0
                day_categories = [0, 1, 2, 3, 4, 5, 6] # Chosen according to weekday indexes of datetime
                day_probabilities = [0.14, 0.15, 0.16, 0.17, 0.16, 0.10, 0.12]
                normalized_probabilities = [p / sum(day_probabilities) for p in day_probabilities]
                sending_day = np.random.choice(day_categories, p=normalized_probabilities)

                if sending_day == 2:
                        sending_day_influence = -0.5
                elif sending_day == 4:
                        sending_day_influence = -0.1
                elif sending_day == 5:
                        sending_day_influence = -0.3
                elif sending_day == 6:
                        sending_day_influence = -0.3

                return sending_day, sending_day_influence
        
        def create_custom_distribution_norm(self, mean, std_dev, skewness, range_min, range_max, size):
                """ 
                Generates custom skew normal distribution with desired range.

                Args
                -------
                mean:                           Desired mean of distribution.
                std_dev:                        Desired standard deviation of distribution.
                range_min:                      Desired range minimum of distribution.
                size:                           Desired amount of samples.

                Returns
                -------
                samples[0]:                     Returns desired sample following defined normal distribution.

                """
                samples = []
                while len(samples) < size:
                        sample_distribution = skewnorm.rvs(skewness, loc=mean, scale=std_dev, size=size-len(samples))
                        for sample in sample_distribution:
                                if sample <= range_max and sample >= range_min:
                                        samples.append(sample)
                                if len(samples) == size:
                                        break
                return samples
        
        def create_mailing_list(simulation_time_days, mailing_frequency_per_month, timestep_size):
                """ 
                Creates mailing list based on input parameters for whole simulation time.
                Mailing list contains dates and Email_Object objects for each date.
                
                Args
                -------
                simulation_time_days:           Counter  for simulation days
                mailing_frequency_per_month:    Specified mailing frequency per month.
                timestep_size:                  Specified time step size.

                Returns
                -------
                mailing_list:                   List of email dispatch dates with defined Email_Object objects.

                """

                mailing_list = []

                mailings_per_month_count = 0
                next_email = Email_Object(1)
                total_mailings = 1
                days_past = 0
                current_time = datetime.now() - timedelta(days=simulation_time_days)
                year_month = current_time.strftime("%Y-%m") 
                month = current_time.strftime("%m")
                end_time = datetime.now()
                while current_time.date() < end_time.date():
                        current_time += timedelta(days=timestep_size)
                        days_past += timestep_size
                        current_weekday = current_time.weekday()
                        if current_time.strftime("%Y-%m") != year_month:
                                mailings_per_month_count = 0
                        
                        month = current_time.strftime("%m")
                        year_month = current_time.strftime("%Y-%m") 
                        if next_email.sending_day == current_weekday and mailings_per_month_count < mailing_frequency_per_month[month]:
                                total_mailings += 1
                                mailings_per_month_count += 1
                                mailing_list.append((next_email, current_time.strftime("%Y-%m-%d")))
                                next_email = Email_Object(total_mailings)
                                
                return mailing_list
