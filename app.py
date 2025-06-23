import streamlit as st
import os

from static import *
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
# @st.cache_data
# def interface_loader(file_paths):
#     """ Load parquet files needed for calculations
#         Loads into st.st.session_state.data_dict
#         (only required 1st time)
#     """
#     def load_file(path):
#         file_name = os.path.basename(path)
#         df = pd.read_parquet(path)
#         return file_name, df

#     data_dict = {}
#     with ThreadPoolExecutor() as executor:
#         results = executor.map(load_file, file_paths)
#         for name, df in results:
#             data_dict[name] = df
#     return data_dict

# @st.cache_data
def interface_loader(file_paths):
    """ Load parquet files one by one, with debug info. """
    st.write("new attempt!")
    data_dict = {}
    for path in file_paths:
        st.write(f"🔄 Loading {path}...")
        try:
            file_name = os.path.basename(path)
            df = pd.read_parquet(path)
            data_dict[file_name] = df
            st.write(f"✅ Loaded {file_name} ({len(df)} rows)")
        except Exception as e:
            st.error(f"❌ Failed to load {path}: {e}")
            raise e  # Optional: crash visibly
    return data_dict

data_dict = interface_loader(file_paths)

all_books = data_dict["all_books_final.parquet"]
all_books_ratings = all_books[['title', 'rating', 'num_ratings']]
books_author_date = all_books[['title', 'author', 'publish_date']]
books_author_date = books_author_date.set_index('title')

users_data = data_dict["users_data.parquet"]
genre_labels = data_dict["genre_labels.parquet"]
all_labeled_reviews = data_dict["all_labeled_reviews.parquet"]
# compact_user_genre_pct = data_dict["compact_user_genre_pct.parquet"]
# main_user_item_matrix = data_dict["main_user_item_matrix.parquet"]

def genre_subtext(title, spaces = 2):
    """ Basic formatting/text function
        (not important)
    """
    for _ in range(spaces):
        st.write("")
    st.write(f"**{title}**")

def set_sliders(genre_values_dict: dict):
    """
    Set slider values (provided by dict)
    """
    for k,v in genre_values_dict.items():
        st.session_state[k] = v
    return

def reset_sliders(default=0):
    for g in fiction_genres:
        st.session_state[g] = default
    for g in nonfiction_genres:
        st.session_state[g] = default
    return

def check_if_sliders_zero():
    for g in fiction_genres + nonfiction_genres:
        if st.session_state[g] != 0:
            return False
    return True

# Slider values are from 0 to max_genre_pct
max_genre_pct = 50

with fiction_sliders:
    st.write("")
    st.subheader("📚 Your personality")
    st.write("")
    
    st.button(
        "Reset",
        on_click=reset_sliders,
        key="reset_sliders"
    )
    
    genre_subtext("Fiction", spaces = 1)

    # Fiction 
    classics = st.slider("Classics", 0, max_genre_pct, key="Classics")
    contemporary = st.slider("Contemporary", 0, max_genre_pct, key="Contemporary")
    fantasy = st.slider("Fantasy", 0, max_genre_pct, key="Fantasy")
    historical_fiction = st.slider("Historical fiction", 0, max_genre_pct, key="Historical Fiction")
    horror = st.slider("Horror", 0, max_genre_pct, key="Horror")
    mystery = st.slider("Mystery", 0, max_genre_pct, key="Mystery")
    romance = st.slider("Romance", 0, max_genre_pct, key="Romance")
    science_fiction = st.slider("Science fiction", 0, max_genre_pct, key="Science Fiction")
    young_adult = st.slider("Young adult", 0, max_genre_pct, key="Young Adult")

with nonfiction_sliders:
    st.subheader("")
    genre_subtext("Nonfiction", spaces = 6)

    # Nonfiction 
    art = st.slider("Art", 0, max_genre_pct, key="Art")
    biography = st.slider("Biography", 0, max_genre_pct, key="Biography")
    business = st.slider("Business", 0, max_genre_pct, key="Business")
    history = st.slider("History", 0, max_genre_pct, key="History")
    music = st.slider("Music", 0, max_genre_pct, key="Music")
    philosophy = st.slider("Philosophy", 0, max_genre_pct, key="Philosophy")
    psychology = st.slider("Psychology", 0, max_genre_pct, key="Psychology")
    science = st.slider("Science", 0, max_genre_pct, key="Science")
    self_help = st.slider("Self help", 0, max_genre_pct, key="Self Help")

fiction_values = [st.session_state[g]/100 for g in fiction_genres]
nonfiction_values = [st.session_state[g]/100 for g in nonfiction_genres]

# ----------------------------- WORKED UP TO THIS POINT (trying load interface) -------------------------------

