import streamlit as st
import os

from get_user_reviews import *
from main_genre_book_recommender import *
from user_review_cache_class import UserReviewCache
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="User Reviews", layout="wide")
fiction_sliders, col2, nonfiction_sliders, col4, col_recommend = st.columns([2, .5, 2, .5, 6]) 

# Preloaded parquet files (for calculations)
file_paths = ["data/all_books_final.parquet",
              "data/users_data.parquet",
              "data/genre_labels.parquet",
              "data/all_labeled_reviews.parquet",
              "data/compact_user_genre_pct.parquet",
              "data/main_user_item_matrix.parquet"]


st.title("Hello")
st.slider("Example", 0,100, key = "slider1")
