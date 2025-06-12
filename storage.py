import pandas as pd
import numpy as np


class Storage:

    def __init__(self,
                 max_vol: float, # max stored value
                 rate: float, # max unit injected/withdrawn per day
                 inj_cost: float, # injection cost per unit
                 wit_cost: float, # withdraw cost per unit
                 cost_per_day_per_unit: float, # cost per day per unit
                 max_days: int = 10000 # maximum number of days in the calendar
                 ):
        self.max_vol = max_vol
        self.rate = rate
        self.inj_cost = inj_cost
        self.wit_cost = wit_cost
        self.cost_per_day_per_unit = cost_per_day_per_unit
        self.predict = False # If True: predict the value of the commodity
                             #          and compute the expected returns
                             # if False: just keep track of the costs
        

        # Initialize variables to keep track of the costs and gains
        self.cost_inj = 0
        self.cost_wit = 0
        self.balance = 0

    def inject(self, vol, date):
        """Inject a given volume in the storage at a given date."""

        # Convert date to int
        t = self._date_to_int(date)

        if float(self.calendar.loc[self.calendar["t"] == t, "vol"].iloc[0]) + vol > self.max_vol:
            raise ValueError(f"Max volume ({vol}) exceded in date {date}.")
        if vol > self.rate:
            raise ValueError(f"Max daily rate exceded in date {date}.")
        
        # Add volume to the storage
        self.calendar.loc[self.calendar["t"] >= t, "vol"] += vol
        
        # Add injection cost to the total cost
        self.cost_inj += self.inj_cost * vol

        if self.predict:
            self.balance -= self.price_func(date) * vol

    def withdraw(self, vol, date):
        """Withdraw a given volume from the storage at a given date."""    

        # Convert date to int
        t = self._date_to_int(date)

        if float(self.calendar.loc[self.calendar["t"] == t, "vol"].iloc[0]) - vol < 0:
            raise ValueError(f"Not enough volume ({vol}) to be withdrawn in date {date}.")
        if vol > self.rate:
            raise ValueError(f"Max daily rate exceded in date {date}.")
        
        # Remove volume from the storage
        self.calendar.loc[self.calendar["t"] >= t, "vol"] -= vol

        # Add withdraw cost to the total cost
        self.cost_wit += self.wit_cost * vol

        if self.predict:
            self.balance += self.price_func(date) * vol

    def prediction_on(self, func):
        """Set the model in prediction mode, by passing
        a function to predict the commodity value."""

        self.price_func = func
        self.predict = True

    def prediction_off(self):
        """Set the model to only compute the costs."""
        self.predict = False

    def process(self, inj_dates, wit_dates, inj_vols, wit_vols):
        """Process all the injections a withdrawals."""

        # Cast the data in dataframes
        inj = pd.DataFrame({"date" : inj_dates, "inj": True, "vol": inj_vols})
        wit = pd.DataFrame({"date" : wit_dates, "inj": False, "vol": wit_vols})
        inj['date'] = pd.to_datetime(inj['date'])
        wit['date'] = pd.to_datetime(wit['date'])
        df = pd.concat([inj, wit], axis=0, ignore_index=True)
        df = df.sort_values(by='date')
        
        # Store the first and last operation dates
        self.first_operation = df['date'].iloc[0]
        self.last_operation = df['date'].iloc[-1]

        # Initialize calendar
        interval = int(self._date_to_int(self.last_operation) - self._date_to_int(self.first_operation))

        self.calendar = pd.DataFrame({"t": np.arange(interval+2), "vol": np.zeros(interval+2)})

        # Process injections/withdrawals
        for row in df.itertuples(index=True):
            if row.inj:
                self.inject(row.vol, row.date)
            else:
                self.withdraw(row.vol, row.date)


        residual_vol = self.calendar.loc[self.calendar["t"] == self._date_to_int(self.last_operation) + 1, "vol"].iloc[0]
        if residual_vol != 0:
            raise ValueError(f"After the last withdrawal the storage is not empty. Residual volume: {residual_vol}.")
        

    def cost_overview(self):
        """Return an overview of the costs."""
        n_days = (self.calendar["vol"] != 0).sum()
        avg_vol = self.calendar["vol"].sum() / n_days
        cost_storage = self.cost_per_day_per_unit * avg_vol * n_days
        total_cost = self.cost_inj + self.cost_wit + cost_storage
        

        avg_cost = total_cost / n_days

        print(f"Costs due to injections: {self.cost_inj}")
        print(f"Costs due to withdrawals: {self.cost_wit}")
        print(f"Storage cost: {cost_storage}")
        print(f"Total day of storage: {n_days}")
        print(f"Total cost: {total_cost}")
        print(f"Average cost per day: {avg_cost}")
        print(f"Avarage volume stored: {avg_vol}")

    def gross_gain(self):
        """Return an overview of the gross_gain, i.e. the gain without the cost subtracted."""
        if not self.predict:
            raise "The model has to be in the predict mode to compute a gain. Use model.prediction_on()."
        
        print(f"Gross gain: {self.balance}")

    def net_gain(self):
        n_days = (self.calendar["vol"] != 0).sum()
        avg_vol = self.calendar["vol"].sum() / n_days
        cost_storage = self.cost_per_day_per_unit * avg_vol
        total_cost = self.cost_inj + self.cost_wit + cost_storage
        print(f"Gross gain: {self.balance}")
        print(f"Total costs: {total_cost}")
        print(f"Net Gain: {self.balance - total_cost}")



    ################# UTILITY FUNCTIONS #######################
    def _date_to_int(self, date):
        """Convert a date to an integer representing the number of days since the first operation."""
        return (pd.Timestamp(date) - pd.Timestamp(self.first_operation)) / pd.Timedelta(days=1) 
    