import configparser
import os
import simpy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from consumer import Consumer
from email_object import Email_Object
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import describe
import json

color_first = "#5372AB"
color_second = "#B65556"

class Simulation:

        def __init__(self):
                """ Initilizes the class with creation of datasets to be created and definition of working directory."""

                path = os.getcwd()
                self.path = os.path.abspath(path).replace(os.sep, "/")
                self.synthetic_dataset = []
                self.opening_data = []
                self.purchase_data = []
                self.global_opening_data = []
                self.global_timespan_data = []
                self.mailings_per_month = {}
                self.purchases_per_month = {}

                # Start the simulation process
                print("Welcome to the Synthetic E-Mail Dataset Simulator!")
                print("Please fill in the config.cfg file and save it.")
                proceed = input("Do you want to start the generation of the synthetic dataset now? [y/n] ")
                if proceed == "y":
                        self.run()
                else:
                        pass

        def run(self):
                """ Instantiates simpy environment. 
                    Reads the input parameters via read_ini. 
                    Passes input parameters to simulation_process and starts it. 
                    Performs analysis after simulation_process completes.

                Args
                -------
                None

                Returns
                -------
                None 

                """
                env = simpy.Environment()
                consumer_amount, simulation_time_days, timestep_size, weekday_names, mailing_frequency_per_month, buying_frequency_per_month, share_buyers, dataset_path, unique_file_path = self.read_ini(self.path+"/config.cfg")

                env.process(self.simulation_process(env, weekday_names, consumer_amount, mailing_frequency_per_month, buying_frequency_per_month, share_buyers, simulation_time_days, timestep_size))
                env.run(until=simulation_time_days)
                proceed = input("Do you want to start analysis of the synthetic dataset now? [y/n] ")
                if proceed == "y":
                        self.data_analysis(consumer_amount, dataset_path, unique_file_path)
                else:
                        pass
        
        def read_ini(self, file_path):
                """ Reads simulation parameters.

                Args
                -------
                file_path: Folder path to config.cfg

                Returns
                -------
                consumer_amount:                Specified consumer amount from config.cfg.
                simulation_time_days:           Specified simulation duration in days from config.cfg.
                weekday_names:                  Specified weekday names to match with weekday numbers of datetime from config.cfg.
                mailing_frequency_per_month:    Specified mailing frequency per month from config.cfg.
                buying_frequency_per_month:     Specified buying frequency per month from config.cfg.
                share_buyers:                   Specified share of buyers from config.cfg.
                dataset_path:                   Specified path to save synthetic dataset to from config.cfg.
                unique_file_path:               Specified path to save unique consumers of  synthetic dataset from config.cfg.
                """

                config = configparser.ConfigParser()
                config.read(file_path)
                consumer_amount = int(config["SIMULATION_PARAMETERS"]["CONSUMER_AMOUNT"])
                simulation_time_days = int(config["SIMULATION_PARAMETERS"]["SIMULATION_TIME_DAYS"])
                timestep_size = int(config["SIMULATION_PARAMETERS"]["TIMESTEP_SIZE"])
                weekday_names = config["SIMULATION_PARAMETERS"]["WEEKDAY_NAMES"]
                mailing_frequency_per_month = json.loads(config["SIMULATION_PARAMETERS"]["MAILING_FREQUENCY_PER_MONTH"])
                buying_frequency_per_month = json.loads(config["SIMULATION_PARAMETERS"]["BUYING_FREQUENCY_PER_MONTH"])
                share_buyers = float(config["SIMULATION_PARAMETERS"]["SHARE_BUYERS"])
                dataset_path = self.path+config["SIMULATION_PARAMETERS"]["DATASET_PATH"]
                unique_file_path = self.path+config["SIMULATION_PARAMETERS"]["UNIQUE_FILE_PATH_"]
                weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

                return consumer_amount, simulation_time_days, timestep_size, weekday_names, mailing_frequency_per_month, buying_frequency_per_month, share_buyers, dataset_path, unique_file_path

        def simulation_process(self, env, weekday_names, consumer_amount, mailing_frequency_per_month, buying_frequency_per_month, share_buyers, simulation_time_days, timestep_size):
                """ Reads simulation parameters from initialization routine.
                    Initializes consumers as well as email and purchase lists.
                    Starts the simulation.

                Args
                -------
                file_path (str): Folder path to config.cfg
                env, weekday_names, consumer_amount, mailing_frequency_per_month, buying_frequency_per_month, share_buyers, simulation_time_days     
                
                Returns
                -------
                None
                """
                time_past, opening_rate, total_mailings, total_purchases, end_time, current_time, year_month, email_dispatch, product_purchase = self.initialize_simulation_parameters(simulation_time_days)

                consumers = Consumer.create_consumers(consumer_amount=consumer_amount)
                
                """
                Create purchase list for purchase dates. 
                """
                purchase_list = Consumer.create_purchase_list(simulation_time_days, buying_frequency_per_month, share_buyers, consumers, timestep_size)
                if purchase_list:
                        next_purchase_date = purchase_list[total_purchases][1].strftime("%Y-%m-%d")
                else:
                        next_purchase_date = 0 

                
                """
                Create mailing list for dispatch dates.
                """
                mailing_list = Email_Object.create_mailing_list(simulation_time_days, mailing_frequency_per_month, timestep_size)
                next_email_dispatch_date = mailing_list[total_mailings][1]
                next_email = mailing_list[total_mailings][0]

                
                """
                Start simulation that starts at current_time which is today - timedelta of simulation_time_days and lasts until today (end_time).
                """
                while current_time.date() < end_time.date():
                        
                        """
                        Timing routine:
                        Increase time by 1 time increment and look for inputs. 
                        """
                        time_past += timestep_size
                        current_time += timedelta(days=timestep_size)

                        if next_email_dispatch_date == current_time.strftime("%Y-%m-%d"):
                                email_dispatch = True
                        else:
                                email_dispatch = False

                        if next_purchase_date == current_time.strftime("%Y-%m-%d"):
                                product_purchase = True
                        else:
                                product_purchase = False

                        # Counter
                        year_month = current_time.strftime("%Y-%m")
                        self.mailings_per_month[year_month] = self.mailings_per_month.get(year_month, 0) 
                        self.purchases_per_month[year_month] = self.purchases_per_month.get(year_month, 0)
                        
                        """
                        Update Routine:
                        Check for occuring dispatch and purchase dates. 
                        Update system and consumer states accordingly.
                        """
                        if email_dispatch == True:
                                campaign_opening_rate = self.email_dispatch(consumers, current_time, next_email, weekday_names)
                                opening_rate += campaign_opening_rate
                                self.opening_data.append((current_time.date(), campaign_opening_rate))
                                total_mailings += 1
                                self.mailings_per_month[year_month] += 1
                                if total_mailings < len(mailing_list):
                                        next_email_dispatch_date = mailing_list[total_mailings][1]
                                        next_email = mailing_list[total_mailings][0]

                        if product_purchase == True:
                                for buyer in purchase_list:
                                        if buyer[1].strftime("%Y-%m-%d") == current_time.strftime("%Y-%m-%d"):
                                                buyer[0].product_purchase = True
                                                buyer[0].purchase_date = current_time.strftime("%Y-%m-%d")
                                                self.purchases_per_month[year_month] += 1
                                                total_purchases += 1
                                        else: 
                                                pass
                                        
                                if total_purchases < len(purchase_list):
                                        next_purchase_date = purchase_list[total_purchases][1].strftime("%Y-%m-%d")

                        if total_mailings > 0:
                                average_opening_rate = opening_rate / total_mailings
                                self.global_opening_data.append((current_time.date(), average_opening_rate))
                                average_timespan = time_past / total_mailings
                                self.global_timespan_data.append((current_time.date(), average_timespan))

                print(  "Anzahl Mailings: ", total_mailings,
                        "\nÖffnungsrate: ", average_opening_rate, 
                        "\nAnzahl Käufe: ", total_purchases, 
                        "\nAnzahl Simulationstage: ", time_past,
                        "\nDurschnittliche Zeitspanne zur letzten E-Mail: ", time_past / total_mailings,
                        "\nMailings pro Monat: ", self.mailings_per_month,
                        "\nKäufe pro Monat: ", self.purchases_per_month)
                
                
                yield env.timeout(1)

        def initialize_simulation_parameters(self, simulation_time_days):
                """ Set initial system states. 
                    Set time step size and set simulation clock to 0.
                    Set counters to 0. 

                Args
                -------
                simulation_time_days: Amount of days for simulation period.

                Returns
                -------
                time_past:              Counter for simulation days.
                opening_rate:           Counter to keep track of opening_rate.
                total_mailings:         Counter for total mailings in simulation.
                total_purchases:        Counter for total purchases in simulation.
                end_time:               Today"s date to stop simulation.
                current_time:           Simulation clock. Set to t - simulation_time_days.
                year_month:             Variable for month of year to simulate time in different years and keep track of mailings and purchases. 
                email_dispatch          
                product_purchase
                """

                end_time = datetime.now()
                current_time = datetime.now() - timedelta(days=simulation_time_days)
                email_dispatch = False
                product_purchase = False
                time_past = 0 # Counter
                opening_rate = 0 # Counter
                total_mailings = 0 # Counter
                total_purchases = 0 # Counter
                year_month = current_time.strftime("%Y-%m") 

                return time_past, opening_rate, total_mailings, total_purchases, end_time, current_time, year_month, email_dispatch, product_purchase
                   
        def email_dispatch(self, consumers, current_time, email, weekday_names):
                """ Timning routine for simulation time interval. 

                Args
                -------
                consumers, current_time, email, weekday_names

                Returns
                -------
                opening_rate: Opening rate of current campaign.
                """  
                
                opens = 0
                for consumer in consumers:
                        """
                        Calculate mailing_frequency and timespan at current simulation time. 
                        """
                        consumer.mailing_frequency = Consumer.calculate_frequency(consumer.mailing_timestamps, current_time)
                        consumer.timespan = Consumer.calculate_timespan(consumer.mailing_timestamps, current_time)

                        """
                        Calculate opening reaction of consumer to email. 
                        """
                        opening, personalization = self.calculate_opening(consumer, email)

                        """
                        Create synthetic data row according to consumers reaction. 
                        """
                        if opening == 1.0:
                                self.synthetic_dataset.append({"consumerID": consumer.consumerID, 
                                                "Alter": consumer.age, 
                                                "Geschlecht": consumer.gender, 
                                                "Einkommen": consumer.income, 
                                                "Informative Wahrnehmung": consumer.informative_perception,
                                                "Frequenz": consumer.mailing_frequency,
                                                "Zeitspanne vorherige E-Mail": consumer.timespan,
                                                "Produktkauf": consumer.product_purchase,
                                                "Öffnung vorherige E-Mail": consumer.prior_email_opening,
                                                "Endgerät": consumer.device,
                                                "emailID": email.emailID,
                                                "Anzahl Wörter in Betreffzeile": email.length,
                                                "Informationsgehalt": email.information_value,
                                                "Personalisierung": personalization,
                                                "Versandtag": weekday_names[current_time.weekday()],
                                                "Simulationszeit": current_time,
                                                "Öffnung": "Ja"})
                                consumer.prior_email_opening = True
                                opens += 1
                        elif opening == 0.0:
                                self.synthetic_dataset.append({"consumerID": consumer.consumerID, 
                                                "Alter": consumer.age, 
                                                "Geschlecht": consumer.gender,
                                                "Einkommen": consumer.income, 
                                                "Informative Wahrnehmung": consumer.informative_perception,
                                                "Frequenz": consumer.mailing_frequency,
                                                "Zeitspanne vorherige E-Mail": consumer.timespan,
                                                "Produktkauf": consumer.product_purchase,
                                                "Öffnung vorherige E-Mail": consumer.prior_email_opening,
                                                "Endgerät": consumer.device,
                                                "emailID": email.emailID,
                                                "Anzahl Wörter in Betreffzeile": email.length,
                                                "Informationsgehalt": email.information_value,
                                                "Personalisierung": personalization,
                                                "Versandtag": weekday_names[current_time.weekday()],
                                                "Simulationszeit": current_time,
                                                "Öffnung": "Nein"})
                                consumer.prior_email_opening = False
                        consumer.mailing_timestamps.append(current_time)
                opening_rate = opens / len(consumers)
                return opening_rate

        def calculate_opening(self, consumer, email):
                """ 
                Calculates the opening reaction of a consumer based on email object. 
                Opening reaction is calculated through logistic regression. 1 = Does open email; 0 = Does not open email.

                Args
                -------
                consumer:               Consumer that receives  email.
                email                   Email that is sent to consumer.

                Returns
                -------
                opening:                Reaction of consumer.                
                personalization:        Personalization status of email object. 
                                        Is decided at the point of dispatch based on consumers purchase state.

                """  

                """
                Calculate the attitude_value for a consumer that receives an email with a certain length
                """
                perceived_value = 0
                if consumer.informative_perception > 0 and email.length > 7:
                        perceived_value = consumer.informative_perception * 1
                elif consumer.informative_perception < 0 and email.length <= 7:
                        perceived_value = consumer.informative_perception * -1
                elif consumer.informative_perception > 0 and email.length <= 7:
                        perceived_value = consumer.informative_perception * -1
                elif consumer.informative_perception < 0 and email.length > 7:
                        perceived_value = consumer.informative_perception * 1
                elif consumer.informative_perception == 0:
                        perceived_value = 0
                
                if consumer.timespan < 3:
                        timespan = consumer.timespan*0.8
                elif consumer.timespan >= 3:
                        timespan = 2.4

                """     
                Set personalization on "Produkbasierte Personalisierung" if consumer has purchased a product. 
                Set influence of personalization, frequency and prior_email_opening according to mediation through product_purchase
                """
                personalization = False
                if consumer.product_purchase == True:
                        personalization = "Produktbasierte Personalisierung"
                        personalization_value = 0.2
                        frequency_influence = 0.3
                        frequency_sqr_influence = -0.1
                        if consumer.prior_email_opening == True:
                                prior_email_opening_influence = 0.7
                        elif consumer.prior_email_opening == False:
                                prior_email_opening_influence = 0
                elif consumer.product_purchase == False:
                        personalization == "Keine Personalisierung"
                        personalization_value = 0
                        frequency_influence = 0.2
                        frequency_sqr_influence = -0.1
                        if consumer.prior_email_opening == True:
                                prior_email_opening_influence = 0.9
                        elif consumer.prior_email_opening == False:
                                prior_email_opening_influence = 0


                """     
                Calculate value for frequency considering the defined formula with frequency and frequency_sqr.
                """
                frequency_value = consumer.mailing_frequency * frequency_influence + consumer.mailing_frequency * consumer.mailing_frequency * frequency_sqr_influence

                """     
                Calculate opening value and opening_probability of the consumer
                """
                opening = np.round(1 / (1 + np.exp(-(-1.6 + perceived_value + personalization_value + email.sending_day_influence + frequency_value + timespan + prior_email_opening_influence + consumer.device_influence))))

                return opening, personalization

        def data_analysis(self, consumer_amount, dataset_path, unique_file_path):
                """ 
                Method to analyze synthetic dataset and save it at desired file path.

                Args
                -------
                consumer_amount:                Specified consumer amount.
                dataset_path:                   Specified path to save synthetic dataset.
                unique_file_path:               Specified path to save unique consumers of  synthetic dataset.

                Returns
                -------
                None

                """  
                df = pd.DataFrame(self.synthetic_dataset)
                df["Simulationszeit"] = pd.to_datetime(df["Simulationszeit"])

                """
                Print stats and create unique_consumers, unique_mails dataset and auxiliary variables.
                """
                unique_consumers = df.drop_duplicates("consumerID")
                unique_consumers.to_csv(unique_file_path, index=False)
                unique_mails = df.drop_duplicates("emailID")
                day_order = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
                unique_mails["Versandtag"] = pd.Categorical(unique_mails["Versandtag"], categories=day_order, ordered=True)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                all_months_time = []
                while start_date <= end_date:
                        if (start_date.day == 1) and (start_date not in all_months_time):
                                all_months_time.append(start_date)
                        start_date += timedelta(days=1)
                all_month_labels = [date.strftime('%m-%Y') for date in all_months_time]

                sns.set(style="ticks")
                age_income_corr = unique_consumers["Alter"].corr(unique_consumers["Einkommen"])
                print("Einkommen \nArithmetisches Mittel:", unique_consumers["Einkommen"].mean(),
                "\nStandardabweichung:", unique_consumers["Einkommen"].std(),
                "\nMedian:", unique_consumers["Einkommen"].median(),
                "\nSchiefe:", describe(unique_consumers["Einkommen"]).skewness,
                "\nWölbung:", describe(unique_consumers["Einkommen"]).kurtosis,
                "\nKorrelation Alter:", age_income_corr)

                print("Alter \nArithmetisches Mittel:", unique_consumers["Alter"].mean(), 
                "\nStandardabweichung:", unique_consumers["Alter"].std(),
                "\nMedian:", unique_consumers["Alter"].median(),
                "\nSchiefe:", describe(unique_consumers["Alter"]).skewness,
                "\nWölbung:", describe(unique_consumers["Alter"]).kurtosis,
                "\nKorrelation Einkommen:", age_income_corr) 


                ###########################          VISUALIZATIONS OF SYNTHETIC DATASET.           ###########################   


                """
                Visualization of timespan between emails in simulation period. 
                """

                time_timespan_global = [entry[0] for entry in self.global_timespan_data]
                number_timespan_global = [entry[1] for entry in self.global_timespan_data]
                
                plt.figure(figsize=(12, 4))
                plt.plot(time_timespan_global, number_timespan_global, color=color_first, label="Durchschnittliche Zeitspanne")
                plt.xlabel("Simulationszeit")
                plt.ylabel("Durchschnittliche Zeitspanne")
                plt.xticks(all_months_time, all_month_labels)
                plt.savefig(self.path+"/results/timespan.png", dpi=300, bbox_inches='tight')
                plt.show()


                """
                Visualization of opening rate in simulation period. 
                """
                number_opening = [entry[1] for entry in self.opening_data]
                average_opening = np.mean(number_opening)
                print(str(average_opening))
                time_opening_global = [entry[0] for entry in self.global_opening_data]
                number_opening_global = [entry[1] for entry in self.global_opening_data]
                plt.figure(figsize=(12, 4))
                plt.plot(time_opening_global, number_opening_global, color=color_first, label="Öffnungsrate")
                plt.xlabel("Simulationszeit")
                plt.ylabel("Öffnungsrate")
                plt.xticks(all_months_time, all_month_labels)
                plt.savefig(self.path+"/results/opening_rate.png", dpi=300, bbox_inches='tight')
                plt.show()

                

                """
                Visualization of mailing frequency per month and purchases per month in synthetic dataset.
                """
                months = list(self.mailings_per_month.keys())
                mailings = list(self.mailings_per_month.values())
                purchases = list(self.purchases_per_month.values())

                fig, ax1 = plt.subplots(figsize=(12, 4))
                ax1.plot(months, mailings, color=color_first, marker="o")
                ax1.set_xlabel("Monat")
                ax1.set_ylabel("Anzahl E-Mails", color=color_first)
                ax1.tick_params("y", colors=color_first)
                ax2 = ax1.twinx()
                ax2.plot(months, purchases, color=color_second, marker="o")
                ax2.set_ylabel("Produktkäufe", color=color_second)
                ax2.tick_params("y", colors=color_second)
                plt.xticks(rotation=90) 
                plt.savefig(self.path+"/results/frequencies.png", dpi=300, bbox_inches='tight')
                plt.show()
                         
                ###########################          VISUALIZATION OF STATIC CONSUMER ATTRIBUTES.           ###########################


                """             
                Visualization of consumer age.
                """
                proportions_age = [0.02*consumer_amount/10, 0.32*consumer_amount/10, 0.35*consumer_amount/10, 0.19*consumer_amount/10, 0.09*consumer_amount/10, 0.03*consumer_amount/10]
                age = [21, 29.5, 39.5, 49.5, 59.5, 69.5]
                plt.figure(figsize=(6, 4))
                plt.plot(age, proportions_age, marker="o", linestyle="-", color=color_second)
                plt.hist(unique_consumers["Alter"], bins=100, color=color_first)
                plt.xlabel("Alter")
                plt.ylabel("Anzahl")
                plt.title("Verteilung des Alters")
                plt.savefig(self.path+"/results/age.png", dpi=300, bbox_inches='tight')
                plt.show()
                

                """             
                Visualization of consumer income.
                """
                income = [4167, 6250, 10417, 14583, 17325, 25000]
                plt.figure(figsize=(6, 4))
                proportions_income = [0.22*consumer_amount/10*2, 0.31*consumer_amount/10*2, 0.21*consumer_amount/10*2, 0.1*consumer_amount/10*2, 0.07*consumer_amount/10*2, 0]
                plt.plot(income, proportions_income, marker="o", linestyle="-", color=color_second, label="Beispielunternehmen")
                plt.hist(unique_consumers["Einkommen"], bins="auto", color=color_first, label="Simulationsmodell")
                plt.xlabel("Einkommen")
                plt.ylabel("Anzahl")
                plt.title("Verteilung des Einkommens")
                plt.savefig(self.path+"/results/income.png", dpi=300, bbox_inches='tight')
                plt.show()

                """             
                Visualization of correlated consumer age and income.
                """
                plt.figure(figsize=(12, 12))
                h = sns.jointplot(x="Alter", y="Einkommen", data=unique_consumers, height=6)
                h.set_axis_labels("Alter", "Einkommen", fontsize=14)
                h.plot_marginals(sns.rugplot)
                plt.savefig(self.path+"/results/age_income_correlation.png", dpi=300, bbox_inches='tight')
                plt.show()

                """
                Visualization of age distributions and device usage in synthetic dataset.
                """
                plt.figure(figsize=(12, 4))
                sns.boxplot(x="Endgerät", y="Alter", data=df)
                plt.xlabel("Endgerät")
                plt.ylabel("Alter")
                plt.savefig(self.path+"/results/devices_age.png", dpi=300, bbox_inches='tight')
                plt.show()



                ###########################          VISUALIZATION OF EMAIL ATTRIBUTES.           ###########################
                unique_mails = df.drop_duplicates("emailID")
                subject_line_length = "Anzahl Wörter in Betreffzeile"
                sending_day = "Versandtag"
                day_order = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
                unique_mails["Versandtag"] = pd.Categorical(unique_mails["Versandtag"], categories=day_order, ordered=True)

                """             
                Visualization of subject line length.
                """
                fig, ax = plt.subplots()
                sns.histplot(data=unique_mails, x=subject_line_length, kde=True, ax=ax, color=color_first)

                value_counts = unique_mails[subject_line_length].value_counts(normalize=True) * 100
                for category, percentage in value_counts.items():
                        ax.text(category, 0, f"{percentage:.1f}%", ha="center", va="bottom", fontsize=8)

                ax.set_xlabel("Anzahl Wörter")
                ax.set_ylabel("Anzahl")
                plt.tight_layout()
                plt.savefig(self.path+"/results/subject_line.png", dpi=300, bbox_inches='tight')
                plt.show()


                """             
                Visualization of sending day.
                """
                fig, ax = plt.subplots()
                sns.histplot(data=unique_mails, x=sending_day, kde=False, ax=ax, color=color_first)

                value_counts = unique_mails[sending_day].value_counts(normalize=True) * 100
                for category, percentage in value_counts.items():
                        ax.text(category, 0, f"{percentage:.1f}%", ha="center", va="bottom", fontsize=8)

                ax.set_xlabel("Versandtag")
                ax.set_ylabel("Anzahl")

                plt.tight_layout()
                plt.savefig(self.path+"/results/sending_day.png", dpi=300, bbox_inches='tight')
                plt.show()
                

                """             
                Save synthetic dataset in desired path.
                """

                #df.to_csv(dataset_path, index=False)

                print("DataFrame saved as CSV file at:", dataset_path)

if __name__ == "__main__":
        simulation = Simulation()