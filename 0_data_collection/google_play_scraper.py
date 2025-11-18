# This script requires the 'google-play-scraper' library.
# Install it first using: pip install google-play-scraper

from google_play_scraper import reviews, Sort
import json

# The app ID from the URL: https://play.google.com/store/apps/details?id=com.nurihaus.lounge
APP_ID = 'com.nurihaus.lounge'
LANGUAGE = 'en'  # Fetch Korean reviews
COUNTRY = 'un'   # Set country to Korea
REVIEW_COUNT = 200 # Number of reviews to fetch

def fetch_app_reviews():
    """
    Fetches reviews for a specific Google Play app.
    """
    print(f"Fetching reviews for app: {APP_ID}...")

    try:
        # Fetch the reviews
        # We sort by NEWEST. You can also use Sort.RATING or Sort.HELPFULNESS.
        result, continuation_token = reviews(
            APP_ID,
            lang=LANGUAGE,
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=REVIEW_COUNT
        )

        if not result:
            print("No reviews found or failed to fetch reviews.")
            return

        print(f"Successfully fetched {len(result)} reviews.\n")

        # Print each review (or process it as needed)
        for i, review in enumerate(result):
            print(f"--- Review {i + 1} ---")
            print(f"User: {review['userName']}")
            print(f"Rating: {review['score']} / 5")
            print(f"Date: {review['at']}")
            print(f"Review Text: {review['content']}")
            
            # Check if there is a developer reply
            if review.get('replyContent'):
                print(f"Developer Reply: {review['replyContent']}")
            
            print("-" * 20 + "\n")

        # You can also save the full result to a JSON file
        # with open('reviews.json', 'w', encoding='utf-8') as f:
        #     json.dump(result, f, ensure_ascii=False, indent=4)
        # print("Saved detailed review data to reviews.json")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_app_reviews()