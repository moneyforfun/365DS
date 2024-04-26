# importing libraries
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin


# introducing classes
class CustomScaler(BaseEstimator, TransformerMixin):

    def __init__(self, columns):
        self.scaler = StandardScaler()
        self.columns = columns
        self.mean_ = None
        self.var_ = None

    def fit(self, X, y=None):
        self.scaler = StandardScaler()
        self.scaler.fit(X[self.columns], y)
        self.mean_ = np.mean(X[self.columns])
        self.var_ = np.var(X[self.columns])
        return self

    def transform(self, X, y=None, copy=None):
        init_col_order = X.columns
        X_scaled = pd.DataFrame(self.scaler.transform(X[self.columns]), columns=self.columns)
        X_not_scaled = X.loc[:, ~X.columns.isin(self.columns)]
        return pd.concat([X_not_scaled, X_scaled], axis=1)[init_col_order]


# creating a class that will be used for new data prediction

class abs_model():

    def __init__(self, model_file, scaler_file):
        # reading in the model and scaler files- files that were saved
        with open('mlmodel', 'rb') as model_file, open('abscaler', 'rb') as scaler_file:
            self.reg = pickle.load(model_file)
            self.scaler = pickle.load(scaler_file)
            self.data = None

    # preprocessing data files-as previously
    def load_and_clean_data(self, data_file):

        df = pd.read_csv('/kaggle/input/df-prep-fixed/df_prep (1).csv', encoding='utf-8')
        # storing data in new variable
        self.df_with_predictions = df.copy()
        df = df.drop(['Unnamed: 0'], axis=1)
        df = df.drop(['ID'], axis=1)
        # preserving code created in the previous section- adding new column with NaN strings
        df['Absenteeism Time in Hours'] = 'NaN'

        # creating separate df with dummy values of all variables
        reason_columns = pd.get_dummies(df['Reason for Absence'], drop_first=True)
        reason_type_1 = reason_columns.loc[:, 1:14].max(axis=1)
        reason_type_2 = reason_columns.loc[:, 15:17].max(axis=1)
        reason_type_3 = reason_columns.loc[:, 18:21].max(axis=1)
        reason_type_4 = reason_columns.loc[:, 22:28].max(axis=1)

        df = df.drop(['Reason for Absence'], axis=1)

        df = pd.concat([df, reason_type_1, reason_type_2, reason_type_3, reason_type_4], axis=1)
        column_names = ['Date', 'Transportation Expense', 'Distance to Work', 'Age',
                        'Daily Work Load Average', 'Body Mass Index', 'Education',
                        'Children', 'Pets', 'Absenteeism Time in Hours', 'Reason_1', 'Reason_2', 'Reason_3', 'Reason_4']
        df.columns = column_names
        column_names_reordered = ['Reason_1', 'Reason_2', 'Reason_3', 'Reason_4', 'Date', 'Transportation Expense',
                                  'Distance to Work', 'Age',
                                  'Daily Work Load Average', 'Body Mass Index', 'Education',
                                  'Children', 'Pets', 'Absenteeism Time in Hours']

        df = df[column_names_reordered]
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        list_mo = []
        for i in range(dfmod.shape[0]):
            list_mo.append(df['Date'][i].month)
        df['Month'] = list_mo
        list_day = []
        list_year = []

        for i in range(dfmod.shape[0]):
            list_day.append(df['Date'][i].weekday())
            list_year.append(df['Date'][i].year)

        df['WeekDay'] = list_day
        df['Year'] = list_year
        df['Education'] = dfmod['Education'].map({1: 0, 2: 1, 3: 1, 4: 1})

        df = df.fillna(value=0)

        df = df.drop(['Date'], axis=1)
        df = df.drop(['Absenteeism Time in Hours', 'WeekDay', 'Daily Work Load Average', 'Distance to Work'], axis=1)

        self.preprocessed_data = df.copy()

        self.data = self.scaler.transform(df)

    def predicted_probability(self):
        if (self.data is not None):
            pred = self.reg.predict_proba(self.data)[:.1]
            return pred

    def predicted_output_category(self):
        if (self.data is not None):
            pred_outputs = self.reg.predict(self.data)
            return pred_outputs

    def predicted_outputs(self):
        if (self.data is not None):
            self.preprocessed_data['Probability'] = self.reg.predict_proba(self.data)[:.1]
            self.preprocessed_data['Prediction'] = self.reg.predict(self.data)