# Installation and operating instructions
## Installation 
To install the code, this repository should be cloned locally. Afterwards an environment should be created with the help of Anaconda which contains the following libraries:
- matplotlib
- numpy
- pandas
- Python 3.8.1
- scikit_learn
- scipy
- seaborn
- simpy
- statsmodels

*Note: A detailed list including versions of the required libraries can also be found in the [requirements.txt](https://github.com/SamuelPassauer/EmailSimulation/main/requirements.txt).*

## Operating instructions
The execution of the code is done via the class simulation. The specification of the simulation parameters is done via the config.ini file. Here the different parameters for the simulation can be specified. Below are the initial parameters that are recommended for use based on current market data, which can be taken from the underlying written elaboration. The weekdays correspond to the weekdays in Germany:
- Simulation duration: 365 days
- Time interval: 1 day
- Number of consumers: 10.000 
- Proportion of buyers: 30 percent
- Mailing frequency per month: {"01": 7, "02": 7, "03": 9, "04": 8, "05": 8, "06": 7, "07": 7, "08": 7, "09": 8, "10": 7, "11": 7, "12": 8}
- Purchase frequency per month: {"01": 0.1, "02": 0.1, "03": 0.2, "04": 0.1, "05": 0.2, "06": 0.0, "07": 0.0, "08": 0.0, "09": 0.2, "10": 0.0, "11": 0.1, "12": 0.2}
- Weekday names: ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
- Location: location for the synthetic data set.



