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


class Recommender:
    def __init__(self):
        self.model = KernelMF(n_epochs=20, n_factors=10, verbose=0, lr=0.001)

    def fit(self, x, y):
        self.model.fit(x, y)
        return self

    def recommend(self, user_id=1):
        return self.model.recommend(user=user_id, amount=ITEMS_NUM_TO_RECOMMEND)[ITEM_ID_COLUMN].to_list()


def generate_not_filled_data(data, user_column, item_column):
    generated_data = pd.DataFrame(itertools.product(data[user_column].unique(), data[item_column].unique()),
                                  columns=[USER_ID_COLUMN, ITEM_ID_COLUMN])
    return generated_data


def calculate_target(full_data, initial_data):
    target = list()
    existed_values = initial_data.values.tolist()
    for idx, value in enumerate(full_data[[USER_ID_COLUMN, ITEM_ID_COLUMN]].values.tolist()):
        target.append(1) if value in existed_values else target.append(0)
    full_data[TARGET] = target
    return full_data


def extract_data_for_user(generated_data, user_id_for_recommendation):
    generated_data = generated_data[
        (generated_data[USER_ID_COLUMN] != user_id_for_recommendation) |
        (generated_data[TARGET] != 0)]
    return generated_data


query = '''SELECT * FROM subs'''
filled_notes_df = pd.read_sql_query(query, connection)

generated_data = generate_not_filled_data(filled_notes_df, 'user_id', 'note_id')
generated_data_with_target = calculate_target(generated_data, filled_notes_df)
generated_data_without_user = extract_data_for_user(generated_data_with_target, user_id_for_recommendation=1)

x_train = generated_data_without_user.drop(TARGET, axis=1)
y_train = generated_data_without_user[TARGET]

recommender = Recommender()
recommender.fit(x_train, y_train)
print('do')
pickle.dump(recommender, open('model.pickle', 'wb'))