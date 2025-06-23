headers_list = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
    },
]


genres = ['Art',
 'Biography',
 'Business',
 'Chick Lit',
 "Children's",
 'Christian',
 'Classics',
 'Comics',
 'Contemporary',
 'Cookbooks',
 'Crime',
 'Ebooks',
 'Fantasy',
 'Fiction',
 'Gay and Lesbian',
 'Graphic Novels',
 'Historical Fiction',
 'History',
 'Horror',
 'Humor and Comedy',
 'Manga',
 'Memoir',
 'Music',
 'Mystery',
 'Nonfiction',
 'Paranormal',
 'Philosophy',
 'Poetry',
 'Psychology',
 'Religion',
 'Romance',
 'Science',
 'Science Fiction',
 'Self Help',
 'Suspense',
 'Spirituality',
 'Sports',
 'Thriller',
 'Travel',
 'Young Adult']

fiction_genres = [
 'Classics',
 'Contemporary',
 'Fantasy',
 'Historical Fiction',
 'Horror',
 'Mystery',
 'Romance',
 'Science Fiction',
 'Young Adult']

nonfiction_genres = [
 'Art',
 'Biography',
 'Business',
 'History',
 'Music',
 'Philosophy',
 'Psychology',
 'Science',
 'Self Help']

lex_genre_dict = {'Classics': 25, 
 'Contemporary': 7, 
 'Fantasy': 17, 
 'Historical Fiction': 7, 
 'Horror': 2, 
 'Mystery': 2, 
 'Romance': 7, 
 'Science Fiction': 15, 
 'Young Adult': 5,
 'Art': 2, 
 'Biography': 12, 
 'Business': 23, 
 'History': 12, 
 'Music': 0, 
 'Philosophy': 38, 
 'Psychology': 35, 
 'Science': 2, 
 'Self Help': 35}

fantasy_girl_dict ={
"Classics":3,
"Contemporary":22,
"Fantasy":50,
"Historical Fiction":25,
"Horror":0,
"Mystery":12,
"Romance":35,
"Science Fiction":6,
"Young Adult":50,
"Art":0,
"Biography":3,
"Business":0,
"History":0,
"Music":3,
"Philosophy":0,
"Psychology":3,
"Science":0,
"Self Help":3
}

profiles = {
    "Lex Fridman": "Deeply curious... always asking the big questions in life.",
    "Aria": "Soft-spoken but adventurous girl with a wild imagination",
}

# Corresponding image paths (replace with actual paths later)
profile_images = {
    "Lex Fridman": "images/lex.png",
    "Aria": "images/aria.png",
}

profile_dicts ={
    "Lex Fridman": lex_genre_dict,
    "Aria": fantasy_girl_dict
}

empty_genre_dict = {g:0 for g in fiction_genres + nonfiction_genres}


# https://www.figma.com/design/ZVbuiFyNCDhtM2fq9sC0T1/Untitled?node-id=1001-3&p=f&t=BVHCCbNdfkEDx1vc-0


rec_df_cols = ['title',
 'author',
 'published',
 'score',
 'rating',
 'count',
 'novelty',
 'goodreads rating',
 'ratings']


neighbor_df_cols = ['user_id',
        'name', 
        'genre similarity', 
        'review samples']