from bs4 import BeautifulSoup
import requests
import re

from static import *
from CustomExceptions import *

def regex_match(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1)

    raise RegexPatternNotFoundException(f"Pattern '{pattern}' not found in the text: {text[:40]}...") 

def remove_comma_from_number(num_str):
    num = num_str.replace(",", "")
    return int(num)


def get_int_from_str(text):
        pattern = r'([\d,]+)'
        match = regex_match(pattern, text)

        num = remove_comma_from_number(match)
        return num

def get_number_from_text(text, dtype = int):
    pattern = r'([\d.]+)'
    match = regex_match(pattern, text)

    if dtype == int:
        return int(match)
    elif dtype == float:
        return float(match)
    else:
        return match

def clean_title_text(title_text):
    cleaned_text = re.sub(r'title|\n', '', title_text).strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    cleaned_text = re.sub(r'\s*\([^)]*\)', '', cleaned_text).strip()

    return cleaned_text


class UserMetaData:
     
    def __init__(self, url, review_pages = 2):
        self.url = url
        self.user_id = url.rsplit('/', 1)[-1]
        self.soup = None

        # intermediate steps
        self.user_stats_html = None

        # basic info
        self.name = None
        self.num_ratings = 0
        self.avg_rating = 0.0
        self.num_reviews = 0

        self.is_best_reviewer = False
        self.reviewer_rank = 0
        
        self.is_most_followed = False
        self.follow_rank = 0    

        # reviews
        self.review_pages = review_pages
        self.review_cards = []
        self.reviews = []


    def retrieve_metadata(self):

        return {
            'user_url': self.url,
            'user_id': self.user_id,
            'name': self.name,
            'num_ratings': self.num_ratings,
            'avg_rating': self.avg_rating,
            'num_reviews': self.num_reviews,
            'is_best_reviewer': self.is_best_reviewer,
            'reviewer_rank': self.reviewer_rank,
            'is_most_followed': self.is_most_followed,
            'follow_rank': self.follow_rank
        }
    
    def retrieve_reviews(self):
        return self.reviews
        
    def set_soup(self, headers_list = headers_list):
        for header in headers_list:
            response = requests.get(self.url, headers=header)
            source = response.text

            if len(source) > 10000:
                soup = BeautifulSoup(source, "lxml")

                if soup:
                    self.soup = soup
                    return True
                
                else:
                    continue

        raise RequestFailedException(f"Failed to fetch URL: {self.url}")
    
    def get_soup(self, url, headers_list = headers_list):
        for header in headers_list:
            response = requests.get(url, headers=header)
            source = response.text

            if len(source) > 10000:
                soup = BeautifulSoup(source, "lxml")

                if soup:
                    return soup
                
                else:
                    continue

        raise RequestFailedException(f"Failed to fetch URL: {url}")


    def get_name_from_html(self):
        soup = self.soup
        name_html = soup.find('h1', class_ = 'userProfileName')
        
        if name_html:
            name = name_html.text
            name = re.sub(r'\n', '', name).strip()
            self.name = name
            return True
        
        raise SoupNotFoundException(f"Couldn't find (h1, class_ = 'userProfileName') from soup")
    

    def get_user_stats_html(self):
        soup = self.soup
        user_stats_html = soup.find('div', class_ = 'profilePageUserStatsInfo')

        if user_stats_html:
            self.user_stats_html = user_stats_html
            return True
        
        raise SoupNotFoundException(f"Couldn't find (div, class_ = 'profilePageUserStatsInfo') from soup")
    

    def get_stats_from_user_stats_html(self):
        links = self.user_stats_html.find_all('a')
        
        if links and len(links) >= 3:
            # ratings
            num_ratings_text = links[0].text
            avg_ratings_text = links[1].text
            num_reviews_text = links[2].text

            self.num_ratings = get_number_from_text(num_ratings_text)
            self.avg_rating = get_number_from_text(avg_ratings_text, dtype = float)
            self.num_reviews = get_number_from_text(num_reviews_text)

            return True

        raise SoupNotFoundException(f"Couldn't find any 'a' links in user_stats_html")
    

    def verify_is_best_reviewer(self):
        best_reviewer_html = self.user_stats_html.find('a', id='tl_best_reviewers')
        
        if best_reviewer_html:
            self.is_best_reviewer = True

            best_reviewer_text = best_reviewer_html.text
            self.reviewer_rank = get_number_from_text(best_reviewer_text)
    
    def verify_is_most_followed(self):
        best_follower_html = self.user_stats_html.find('a', id='tl_most_followed')

        if best_follower_html:
            self.is_most_followed = True

            best_follower_text = best_follower_html.text
            self.follow_rank = get_number_from_text(best_follower_text)


    def get_metadata(self):
        try:
            self.set_soup()  
        except Exception as e:
            print(f"Error in set_soup: {e}")
            return  
        
        try:
            self.get_name_from_html() 
        except Exception as e:
            print(f"Error in get_name_from_html: {e}")


        try:
            self.get_user_stats_html()
        except Exception as e:
            print(f"Error in get_user_stats_html: {e}")
            return  
        
        methods = [
            self.get_stats_from_user_stats_html,
            self.verify_is_best_reviewer,
            self.verify_is_most_followed
        ]
    
        for method in methods:
            try:
                method()  
            except Exception as e:
                print(f"Error in {method.__name__} for {self.user_id}: {e}")
                continue  

    
    def get_review_cards_single_page(self, user_id, i):
        url = f'https://www.goodreads.com/review/list/{user_id}?page={i}&sort=votes&view=reviews'
        soup = self.get_soup(url)
        
        if soup:
            review_cards = soup.find_all('tr', class_ = 'bookalike review')
            return review_cards
        
        return None
    
    def get_review_cards(self, user_id):
        all_review_cards = []

        # make sure we don't look at empty pages
        n = self.review_pages
        n = min(n, self.num_ratings // 20) + 1

        for i in range(1, n + 1):
            review_cards = self.get_review_cards_single_page(user_id, i)
            all_review_cards.extend(review_cards)

        self.review_cards = all_review_cards

    def get_title_from_review_card(self, review_card):

        title_html = review_card.find('td', class_ = 'field title')
        if title_html:
            title_text = title_html.text
            title_text = clean_title_text(title_text)

            return title_text
        
        raise SoupNotFoundException(f"Couldn't find (td, field title) from review card")
    

    def get_title_url_from_review_card(self, review_card):
        base_url = 'https://www.goodreads.com'

        title_html = review_card.find('td', class_ = 'field title')
        if title_html:
            try:
                title_url = title_html.a['href']
                title_url = title_url.rsplit('/', 1)[-1]
                
                return title_url
            except Exception as e:
                raise SoupNotFoundException(f"title url from review card error: {e}")

        raise SoupNotFoundException(f"Couldn't find (td, field title) from review card")
    
        
    def get_rating_from_review_card(self, review_card):
        rating_html = review_card.find('td', class_ = 'field rating')
        if rating_html:
            star_count_html = rating_html.find_all('span', class_ = 'staticStar p10')
            rating = len(star_count_html)       
            return rating
        
        raise SoupNotFoundException(f"Couldn't find (td, field rating) from review card")
    
    def get_rating_votes_from_review_card(self, review_card):
        votes_html = review_card.find('td', class_ = 'field votes')
        if votes_html:
            votes_text = votes_html.text
            votes = get_number_from_text(votes_text)
            return votes
        
        raise SoupNotFoundException(f"Couldn't find (td, field votes) from review card")
    
    def get_review_card_info(self, review_card):
        # Initialize review_card_dict with user_id
        review_card_dict = {'user_id': self.user_id}

        methods = [
            (self.get_title_url_from_review_card, 'title_id'),
            (self.get_title_from_review_card, 'title'),
            (self.get_rating_from_review_card, 'rating'),
            (self.get_rating_votes_from_review_card, 'votes')
        ]
        
        # Loop through each method and handle exceptions individually
        for method, dict_key in methods:
            try:
                result = method(review_card)
                review_card_dict[dict_key] = result
            except Exception as e:
                print(f"Error in {method.__name__} for review card: {e}")
                continue  
        
        return review_card_dict
        

    def get_reviews(self):
        try:
            reviews = [self.get_review_card_info(review) for review in self.review_cards]
            self.reviews = reviews

        except SoupNotFoundException as e:
            print(f"SoupNotFound error in get_reviews(): {e}")
        except RegexPatternNotFoundException as e:
            print(f"RegexNotFound error in get_reviews(): {e}")
        except Exception as e:
            print(f"Unexpected error in get_reviews(): {e}")

    def get_review_info(self):
        
        self.get_review_cards(user_id = self.user_id)
        
        try:
            self.get_review_cards(user_id = self.user_id)
        except Exception as e:
            print(f"Error in get_review_cards(): {e}")
        else:
            self.get_reviews()

    def set_review_cards(self, review_cards):
        self.review_cards = review_cards
        return

    


# def test(url):
#     user = UserMetaData(url, review_pages=4)
#     user.get_metadata()

#     user_metadata = user.retrieve_metadata()
#     print("--- User metadata ---")
#     print(user_metadata)
#     print()

#     user.get_review_info()
#     user_reviews = user.retrieve_reviews()
#     print("--- User reviews ---")
#     print(user_reviews)
#     print(len(user_reviews))

# url = 'https://www.goodreads.com/user/show/159234716-zo'

# url = 'https://www.goodreads.com/user/show/153156500-michelle-lee'
# test(url)