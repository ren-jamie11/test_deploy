import pandas as pd
import numpy as np
import time

from static import *
from sklearn.metrics.pairwise import cosine_similarity

def get_user_genre_counts(reviews):
    
    user_genre_counts = reviews.groupby('user_id')[genres].sum().T  # genres as index
    num_reviews_by_user = reviews.groupby('user_id')['title'].count()
    user_genre_pct = user_genre_counts.div(num_reviews_by_user, axis = 1)

    return user_genre_counts, user_genre_pct

""" Local data files """

print("Loading parquets...")
start = time.time()

all_books = pd.read_parquet("data/all_books.parquet")
all_books['publish_date'] = all_books['publish_date'].str[:-6]
all_books_ratings = all_books[['title', 'rating', 'num_ratings']]
books_author_date = all_books[['title', 'author', 'publish_date']]
books_author_date = books_author_date.set_index('title')

users_data = pd.read_parquet("data/users_data.parquet")

genre_labels = pd.read_parquet("data/genre_labels.parquet")
all_labeled_reviews = pd.read_parquet("data/all_labeled_reviews.parquet")
user_genre_counts, user_genre_pct = get_user_genre_counts(all_labeled_reviews)
compact_user_genre_pct = pd.read_parquet("data/compact_user_genre_pct.parquet")
main_user_item_matrix = pd.read_parquet("data/main_user_item_matrix.parquet")

end = time.time()
print(f"Finished loading parquets in {(end - start):.1f} seconds!")

""" Functions """
def get_expert_user_item_matrix(user_item_matrix, experts):
    expert_user_item_matrix =  user_item_matrix[user_item_matrix.index.isin(experts)]
    expert_user_item_matrix = expert_user_item_matrix.loc[experts]

    return expert_user_item_matrix

def get_expert_ratings(expert_user_item_matrix, top_n_reviewers):
    """ sum(amount of say * rating) for everyone who rated the book for each book
    
    The more people who interacted...the more the score will be affected
    E.g. 10 people who rated positive > 5 people who rated positive
    """
    amount_of_say = top_n_reviewers['score_normed']

    expert_ratings = expert_user_item_matrix.T.dot(amount_of_say)
    expert_ratings= pd.DataFrame(expert_ratings)
    
    expert_ratings.columns = ['expert_metric']
    expert_ratings = expert_ratings.drop_duplicates()
    expert_ratings = expert_ratings.sort_values(by = 'expert_metric', ascending = False)

    return expert_ratings

def lookup_rating(user_item_matrix, user_id, book_name):
    return user_item_matrix.loc[user_id, book_name]

def ratings_of_those_who_read(book_name, top_n_reviewers, expert_user_item_matrix):
    experts = top_n_reviewers.index
    amount_of_say = top_n_reviewers['score_normed']
    
    wavgs = pd.DataFrame(amount_of_say)
    wavgs['book_rating'] = [lookup_rating(expert_user_item_matrix, u, book_name) for u in experts]
    wavgs = wavgs[wavgs.book_rating != 0]

    return wavgs

def avg_expert_rating(book_name, top_n_reviewers, expert_user_item_matrix):
    amount_of_say = top_n_reviewers['score_normed']
    experts = top_n_reviewers.index
    
    wavgs = ratings_of_those_who_read(book_name, top_n_reviewers, expert_user_item_matrix)
    res = np.dot(wavgs['score_normed'], wavgs['book_rating'])/np.sum(wavgs['score_normed'])
    
    return res, len(wavgs)

def get_score(count, pct, alpha = 1):
    score = count * pct**alpha
    return score

def min_max_scale(series, max_value = 100):
    min_val = series.min()
    max_val = series.max()
    return ((series - min_val) / (max_val - min_val)) * max_value

def normalize_series(series):
    mean = series.mean()
    std = series.std()
    return (series - mean) / std

def label_reviews_with_genre(all_reviews, genre_labels):
    all_labeled_reviews = all_reviews.merge(
        genre_labels, 
        on='title', 
        how='inner'
    )

    all_labeled_reviews = all_labeled_reviews.drop_duplicates(subset=['title', 'user_id', 'rating'])
    return all_labeled_reviews

def user_read_counts_for_genre(my_genre, user_genre_counts, user_genre_pct):
    genre_review_count_ranked = user_genre_counts.loc[my_genre, :].sort_values(ascending = False)
    genre_pct_of_reviews_ranked = user_genre_pct.loc[my_genre, :].sort_values(ascending = False)

    res = pd.DataFrame({"review_count": genre_review_count_ranked, "review_pct": genre_pct_of_reviews_ranked})
    return res

def get_genre_ranker(my_genre, user_genre_counts, user_genre_pct, alpha = 1, allowed = main_user_item_matrix.index):
    """ Ranks all reviewers for a genre in a df

    Schema
    ---------------------------------------------------
    user_id  | review_count   review_pct   score
    ----------------------------------------------------

    review_count: How many books have they reviewed from this genre?
    review_pct: What % of the books they've reviewed are from this genre?
    score: Weighted combination of count and pct (count * pct ** alpha) 
    
    """
    
    user_read_counts = user_read_counts_for_genre(my_genre, user_genre_counts, user_genre_pct)
    user_read_counts['score'] = get_score(user_read_counts['review_count'], user_read_counts['review_pct'], alpha = alpha)

    user_read_counts = user_read_counts[user_read_counts.review_count > 0]
    user_read_counts = user_read_counts.sort_values(by = 'score', ascending = False)

    user_read_counts = user_read_counts[user_read_counts.index.isin(allowed)]
    
    return user_read_counts

def get_top_n_reviewers(ranker, n):
    n = min(n, len(ranker))
    print("n", n)
    top_n = ranker.head(n)
    top_n['score_normed'] = top_n['score']/np.sum(top_n['score'])

    return top_n

def get_user_genre_counts_and_pcts(user_reviews, genre_labels = genre_labels):
    this_user_reviews_labeled = label_reviews_with_genre(user_reviews, genre_labels)
    this_user_genre_counts, this_user_genre_pct = get_user_genre_counts(this_user_reviews_labeled)

    return this_user_genre_counts, this_user_genre_pct

def get_user_similarities_ranker_by_genre(this_user_genre_pct, alpha, min_similarity = 0.8, user_genre_counts = user_genre_counts, 
                                          other_users_genre_pct = compact_user_genre_pct):
    # construct matrix
    M = other_users_genre_pct.values
    v = this_user_genre_pct.values
    similarities = cosine_similarity(M.T, v.T).ravel()
    other_users = other_users_genre_pct.T.index
    similarity_ranker = pd.DataFrame({'other_users': other_users, 'genre_similarity': similarities})
    
    # Formatting the similarity table
    similarity_ranker = similarity_ranker.set_index("other_users")
    similarity_ranker['read_count'] = user_genre_counts.sum(axis = 0)
    similarity_ranker = similarity_ranker[similarity_ranker.genre_similarity >= min_similarity]
    similarity_ranker['score'] = get_score(similarity_ranker['read_count'], similarity_ranker['genre_similarity'], alpha = alpha)
    similarity_ranker = similarity_ranker.sort_values(by = 'score', ascending = False) 
    
    return similarity_ranker


def get_author_for_recs(recs, books_author_date = books_author_date):
    assert recs.index.name == 'title', "Recs index must be title"
    assert books_author_date.index.name == 'title', "books/author df index must be title"
    
    recs = recs.merge(books_author_date, left_index = True, right_index = True)
    author_col = recs.pop('author')
    recs.insert(0, 'author', author_col)
    
    return recs

def recommend_books_by_user_genre_reading_pattern_similarity(user_reviews, novelty_factor, alpha = 250, genre_labels = genre_labels):
    if len(user_reviews) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    # get similar users
    this_user_genre_counts, this_user_genre_pct = get_user_genre_counts_and_pcts(user_reviews, genre_labels = genre_labels)
    
    """ USE THIS FOR CUSTOME GENRE PCT"""
    genre_similarity_ranker = get_user_similarities_ranker_by_genre(this_user_genre_pct, alpha = alpha)

    recommended_books, neighbors = get_recommendation_from_top(genre_similarity_ranker, novelty_factor)
    recommended_books = recommended_books[~recommended_books.index.isin(user_reviews.title.values)]
    
    return recommended_books, neighbors

def get_url_from_user_id(user_id):
    user_row = users_data[users_data.user_id == user_id]
    if user_row:
        url = user_row['user_url'].values[0]
        return url

    return "user url not found..."

def get_book_scores_from_experts(user_item_matrix, rating_emphasis):
    """
    Given a user-item rating matrix with users as rows and book titles as columns,
    returns a DataFrame with the mean rating and number of ratings per book,
    ignoring zero entries.
    """

    masked = user_item_matrix.mask(user_item_matrix == 0)
    
    avg_ratings = masked.mean(axis=0)
    rating_counts = masked.count(axis=0)

    book_stats = pd.DataFrame({
        "rating": avg_ratings,
        "count": rating_counts
    })

    book_stats = book_stats.dropna(subset=["rating"])
    book_stats['score'] = get_score(book_stats['count'], book_stats['rating'], alpha = rating_emphasis)
    book_stats['score'] = min_max_scale(book_stats['score']).round(1)
    book_stats = book_stats.sort_values(by="score", ascending=False)
    book_stats = book_stats[['score', 'rating', "count"]]

    return book_stats

def merge_expert_with_overall(expert_rating, all_books_rating, num_reviewers):
    merged = expert_rating.merge(all_books_ratings, left_index=True, right_on='title', how='inner')
    merged = merged.set_index('title')
    
    return merged

def format_thousands(series):
    """
    Convert integers to strings formatted in thousands with 'k' suffix.
    Examples:
        12345 -> '12.3k'
        24992 -> '25k'
        300   -> '0.3k'
    """
    return series.apply(lambda x: f"{x/1000:.1f}k".rstrip('0').rstrip('.'))

def filter_book_recs_by_score_or_n(df, n, min_score):
    high_score_books = df[df.score >= min_score]
    if len(high_score_books) >= n:
        return high_score_books.head(n)

    return high_score_books


def get_bin_labels(arr, width = 0.001):
    quantiles = np.arange(0.1, 1.0, width)
    quantile_values = np.quantile(arr, quantiles)

    bin_indices = np.digitize(arr, quantile_values, right=True)
    bin_indices = np.clip(bin_indices, 0, len(quantiles) - 1)
    bin_labels = quantiles[bin_indices].round(2)

    return bin_labels


def enrich_books_with_metadata(recommended_books, book_ratings = all_books_ratings, metadata = books_author_date):
    merged = recommended_books.merge(book_ratings, left_index=True, right_on='title', how='inner')
    merged = merged.set_index('title').rename(columns = {'rating_x': 'rating', 'rating_y': 'overall_rating'})
    merged_with_book_data = pd.merge(metadata, merged, left_index = True, right_index = True, how = 'right')

    return merged_with_book_data


def post_process_books(recommended_books, n = 50):
    recommended_books = recommended_books[['author', 'publish_date', 'adjusted_score','rating', 'count', 'novelty', 'overall_rating', 'num_ratings']] 
    recommended_books.columns = ['author', 'published', 'score','rating', 'count', 'novelty', 'goodreads rating', 'ratings']
    recommended_books = recommended_books.drop_duplicates(subset = ['author', 'published', 'goodreads rating'])
    recommended_books['score'] = recommended_books['score'].round(1) 
    recommended_books['rating'] = recommended_books['rating'].round(1) 
    recommended_books['goodreads rating'] = recommended_books['goodreads rating'].round(1) 
    recommended_books['ratings'] = format_thousands(recommended_books['ratings'])

    return recommended_books.head(50).sort_values(by = 'score', ascending = False)

def post_process_neighbors(neighbors, users_data = users_data):
    user_cols = ['name','genre_similarity', 'read_count']

    m_neighbors = pd.merge(neighbors, users_data, left_index = True, right_on = "user_id", how = "left")
    m_neighbors['genre_similarity'] = m_neighbors['genre_similarity'].round(3) 
    m_neighbors = m_neighbors.set_index('user_id')
    m_neighbors = m_neighbors[user_cols]

    m_neighbors.columns = ['name', 'genre similarity', 'review samples']
    
    return m_neighbors

def get_recommendation_from_top(ranker, novelty_factor, user_item_matrix = main_user_item_matrix,
                                num_reviewers = 100, rating_emphasis = 2, min_similarity = 0.85):
    
    top_n = get_top_n_reviewers(ranker, num_reviewers)
    top_n = top_n[top_n.genre_similarity >= min_similarity]
    experts = top_n.index
    neighbors = post_process_neighbors(top_n.head(num_reviewers))
    
    # user_item_matrix for top reviewers of this genre
    expert_user_item_matrix = get_expert_user_item_matrix(user_item_matrix, experts)
    expert_ratings = get_book_scores_from_experts(expert_user_item_matrix, rating_emphasis)

    rec_books_with_metadata = enrich_books_with_metadata(expert_ratings)
    rec_books_with_metadata['novelty'] = get_bin_labels(rec_books_with_metadata.num_ratings.values)
    rec_books_with_metadata['novelty'] = np.abs(1 - rec_books_with_metadata['novelty'])
    rec_books_with_metadata['adjusted_score'] = get_score(count = rec_books_with_metadata['score'],
                                                          pct = rec_books_with_metadata['novelty'],
                                                          alpha = novelty_factor)
    
    rec_books_with_metadata['adjusted_score'] = min_max_scale(rec_books_with_metadata['adjusted_score'])
    best_books = post_process_books(rec_books_with_metadata)

    
    return best_books, neighbors

