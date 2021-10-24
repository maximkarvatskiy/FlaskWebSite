import sqlalchemy
import sqlite3 as sql
import pandas as pd
import numpy as np
from matrix_factorization import KernelMF, train_update_test_split
import itertools
import pickle

TARGET = 'target'
USER_ID_COLUMN = 'user_id'
ITEM_ID_COLUMN = 'item_id'
ITEMS_NUM_TO_RECOMMEND = 5

database = 'website/database.db'
connection = sql.connect(database)

query = '''SELECT * FROM subs'''
records_df = pd.read_sql_query(query, connection)


class Recommender():
    def __init__(self, user_id_for_recommendation):
        self.user_id_for_recommendation = user_id_for_recommendation
        self.generated_data = pd.DataFrame()
        self.model = KernelMF(n_epochs=20, n_factors=2, verbose=1, lr=0.001)

    def fit(self, data, user_column, item_column):
        self.generate_possible_combinations(data, user_column, item_column)
        self.generate_target(data)
        self.extract_data_for_user()

        x_train = self.generated_data.drop(TARGET, axis=1)
        y_train = self.generated_data[TARGET]
        self.model.fit(x_train, y_train)
        return self

    def recommend(self, user_id=1):
        return self.model.recommend(user=1, amount=ITEMS_NUM_TO_RECOMMEND)[ITEM_ID_COLUMN].to_list()

    def generate_possible_combinations(self, data, user_column, item_column):
        self.generated_data = pd.DataFrame(itertools.product(data[user_column].unique(), data[item_column].unique()),
                                           columns=[USER_ID_COLUMN, ITEM_ID_COLUMN])
        return self

    def generate_target(self, data):
        target = list()
        existed_values = data.values.tolist()
        for idx, value in enumerate(self.generated_data[[USER_ID_COLUMN, ITEM_ID_COLUMN]].values.tolist()):
            target.append(1) if value in existed_values else target.append(0)
        self.generated_data[TARGET] = target
        return self

    def extract_data_for_user(self):
        self.generated_data = self.generated_data[
            (self.generated_data[USER_ID_COLUMN] != self.user_id_for_recommendation) |
            (self.generated_data[TARGET] != 0)]
        return self


recommender = Recommender(user_id_for_recommendation=1)
recommender.fit(data=records_df, user_column='user_id', item_column='note_id')

pickle.dump(recommender, open('website/recommender.pickle', 'wb'))
