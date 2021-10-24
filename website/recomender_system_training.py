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
LIKED = 1
DISLIKED = 0

database = 'website/database.db'
connection = sql.connect(database)


class Recommender:
    """Class for generate recommendation for user.

       Attributes:
           model: recommendation system object.
           known_users: users for beat cold start problem
           top_rated_items: items for new users
       """
    def __init__(self):
        """Initiate Recommender class"""
        self.model = KernelMF(n_epochs=20, n_factors=10, verbose=0, lr=0.001)
        self.known_users = list()
        self.top_rated_items = list()

    def fit(self, x, y):
        """
        Fits on actual data.
        todo: Saving information about known users and most popular items for solving cold start problem
        """
        self.model.fit(x, y)
        return self

    def recommend(self, user_id=1):
        """
        Generate a recommendation for selected user.

        Args:
          user_id: user index recommendation generating.

        Returns: A list of recommendation item indexes
        """
        recommendations = self.model.recommend(user=user_id, amount=ITEMS_NUM_TO_RECOMMEND)
        recommendations_items = recommendations[ITEM_ID_COLUMN].to_list()
        return recommendations_items


def generate_not_filled_data(data: pd.DataFrame, user_column: str, item_column: str)->pd.DataFrame:
    """
    Create dataframe and fill all unknown user-note combinations as disliked
    needed for generating correct data for training.

    Args:
      data: actual data with user-note combinations.
      user_column: user column name for passing into recommendation system.
      item_column: item column name for passing into recommendation system.

    Returns: Generated dataframe with filled unknown user-note combinations
    """
    generated_data = pd.DataFrame(itertools.product(data[user_column].unique(), data[item_column].unique()),
                                  columns=[USER_ID_COLUMN, ITEM_ID_COLUMN])
    return generated_data


def calculate_target(full_data: pd.DataFrame, initial_data: pd.DataFrame)->pd.DataFrame:
    """
       Generate liked or not target column for all user-note pairs.

       Args:
         full_data: data with generated all user-note pairs.
         initial_data: actual data with user-note combinations.

       Returns: dataframe with target column
       """
    target = list()
    existed_values = initial_data.values.tolist()
    for idx, value in enumerate(full_data[[USER_ID_COLUMN, ITEM_ID_COLUMN]].values.tolist()):
        target.append(LIKED) if value in existed_values else target.append(DISLIKED)
    full_data[TARGET] = target
    return full_data


def extract_data_for_user(generated_data:pd.DataFrame, user_id_for_recommendation:int)->pd.DataFrame:
    """
       Tricky think to drop current user from all pairs to be able to make a recommendation.

       Args:
         generated_data: data with generated all user-note pairs and target.
         user_id_for_recommendation: current user index.

       Returns: dataframe with extracted information about unknown notes for current user
       """
    generated_data = generated_data[
        (generated_data[USER_ID_COLUMN] != user_id_for_recommendation) |
        (generated_data[TARGET] != DISLIKED)]
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

pickle.dump(recommender, open('website/model.pickle', 'wb'))
