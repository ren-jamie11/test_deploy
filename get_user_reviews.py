from static import headers_list
from UserScraper import *

import aiohttp
import asyncio
import time



def get_review_cards_single_page(self, user_id, i):
    url = f'https://www.goodreads.com/review/list/{user_id}?page={i}&sort=votes&view=reviews'
    soup = self.get_soup(url)
    
    if soup:
        review_cards = soup.find_all('tr', class_ = 'bookalike review')
        return review_cards
    
    return None


async def load_user_reviews_from_single_url(url, session, 
                                            headers = headers_list, 
                                            time_out = 3.5,
                                            attempts = 3):
    
    start = time.time()
    attempts = max(attempts, len(headers))
    for i in range(attempts):
        try:
            async with session.get(url, headers = headers[i], timeout = time_out) as response:

                # if i == 0:
                #     async def fake_text():
                #         await asyncio.sleep(10)
                #         return "<html>should never return</html>"
                #     response.text = fake_text  # override method
                # last attempt can take longer

                if i < attempts - 1:
                    source = await asyncio.wait_for(response.text(), timeout=time_out)
                else:
                    source = await response.text()
                
        except asyncio.TimeoutError:
            print(f"Timeout while loading {url} on attempt {i}")
            continue

        except Exception as e:
            print(f"Error with URL {url} on attempt {i}: {e}")
            continue

        if len(source) > 10000:
            end = time.time()
            print(f"Time taken: {end - start}")
            soup = BeautifulSoup(source, "lxml")
            review_cards = soup.find_all('tr', class_ = 'bookalike review')
            return review_cards
        
        print(f"Parsed faulty url on attempt {i}")

    raise RuntimeError(f"Failed to fetch URL {url} after {attempts} attempts")


def get_user_review_page_url(user_id, i):
    return f'https://www.goodreads.com/review/list/{user_id}?page={i}&sort=votes&view=reviews'

def get_user_profile_url(user_id):
    return f"https://www.goodreads.com/user/show/{user_id}"

user_id = '155041466-jamie-ren'
page = 1

user_profile_url = get_user_profile_url(user_id)


async def main(user_id, pages = 5):
    urls = [get_user_review_page_url(user_id, i) for i in range(1, pages + 1)]
    start = time.time()
    async with aiohttp.ClientSession() as session:
        # Schedule all fetch coroutines concurrently
        tasks = [load_user_reviews_from_single_url(url, session) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end = time.time()
        elapsed = end - start

        results = [r for r in results if not isinstance(r, Exception)]

        return results

""" Next: Load the reviews into a DataFrame"""

def get_reviews_from_user_url(user_id):
    results = asyncio.run(main(user_id))
    flattened = [review for page in results for review in page if review]

    user_profile_url = get_user_profile_url(user_id)
    user = UserMetaData(user_profile_url, review_pages = 4)
    user.set_review_cards(flattened)
    user.get_reviews()
    user_reviews = user.retrieve_reviews()

    return user_reviews



""" Test """
# user_reviews = get_reviews_from_user_url(user_id)

