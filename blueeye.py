# === Import necessary libraries ===
import tweepy
import requests
from bs4 import BeautifulSoup
import os
import datetime
import pytz
import jdatetime
import schedule
from openai import OpenAI
from tKEYS import *

# === Twitter and OpenAI configuration ===
API_KEY = APIKEY
API_SECRET_KEY = APIKEYSECRET
ACCESS_TOKEN = ACCESSTOKEN
ACCESS_TOKEN_SECRET = ACCESSTOKENSECRET
TWITTER_HANDLE = id
DIGIATO_LINKS_FILE = "t_digiato_sent_links.txt"
OPENAI_API_KEY = oaien

# === Initialize OpenAI API client ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Initialize Twitter API clients (v1.1 for media, v2 for tweets) ===
try:
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    twitter_api_v1 = tweepy.API(auth)  # Used for media upload
    twitter_client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    print("Starting X bot")
except Exception as e:
    print("Twitter API initialization failed:", e)
    exit(1)

# === Daily images for calendar posts ===
day_images = ["tsat.png", "tsun.png", "tmon.png", "ttue.png", "twed.png", "tthur.png", "tfri.png"]

# === Fetch latest Digiato article links from homepage ===
def fetch_digiato_links():
    print("fetch_digiato_links")
    try:
        html = requests.get("https://digiato.com/").text
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select('a.rowCard__title[href^="https://digiato.com/"]')
        links = []
        for a in anchors:
            href = a["href"]
            if href.startswith("https://digiato.com/") and href not in links:
                links.append(href)
            if len(links) >= 5:
                break
        return links
    except Exception as e:
        print("Error fetching links:", e)
        return []

# === Extract keywords from Digiato article URL for summarization ===
def extract_keywords_from_url(url):
    print("extract_keywords_from_url")
    base_url = "https://digiato.com/"
    if url.startswith(base_url):
        path = url[len(base_url):].strip('/')
    else:
        path = url
    keywords = path.replace('-', ' ').split()
    return ' '.join(keywords)

# === Generate relevant English tech hashtags using OpenAI ===
def generate_hashtags(content):
    try:
        prompt = f"""بر اساس محتوای زیر، دو هشتگ مرتبط با موضوع تکنولوژی به زبان انگلیسی تولید کنید. هشتگ‌ها باید کوتاه، مرتبط و مناسب برای توییتر باشند.

        محتوا: {content}

        پاسخ: دو هشتگ در قالب لیست، مانند ["#Tech", "#Innovation"]"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50,
        )
        hashtags = response.choices[0].message.content.strip()
        hashtags = hashtags.strip('[]').replace('"', '').split(', ')
        return hashtags if len(hashtags) >= 2 else ["#Technology", "#Innovation"]
        print("generate_hashtags")  # Unreachable code
    except Exception as e:
        print("Hashtag generation failed:", e)
        return ["#Tech", "#Innovation"]

# === Summarize article using OpenAI and generate tweet text ===
def summarize_article(url):
    try:
        keywords = extract_keywords_from_url(url)
        prompt = f"""از کلمات زیر برای تولید یک خلاصه‌ی تحلیلی کوتاه و جذاب به زبان فارسی برای شبکه‌های اجتماعی استفاده کنید. خلاصه باید حداکثر 100 کاراکتر، در حداکثر 5 سطر باشد و برای توییتر مناسب باشد. موضوع درباره تکنولوژی است.

        کلمات: {keywords}

        پاسخ:"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50,
        )
        summary = response.choices[0].message.content.strip()
        hashtags = generate_hashtags(summary)
        twitter_summary = f"{summary}\n{' '.join(hashtags)}\n{url}\n📡"
        print("summarize_article")
        return twitter_summary
    except Exception as e:
        print("Article summarization failed:", e)
        return ""

# === Load previously tweeted links from local file ===
def load_digiato_sent_links():
    if not os.path.exists(DIGIATO_LINKS_FILE):
        return set()
    with open(DIGIATO_LINKS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# === Save newly tweeted links to local file ===
def save_digiato_sent_links(links):
    with open(DIGIATO_LINKS_FILE, "a", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

# === Post the most relevant news article to Twitter ===
def post_article():
    sent_links = load_digiato_sent_links()
    new_links = [link for link in fetch_digiato_links() if link not in sent_links]

    if new_links:
        link = select_most_important_link(new_links)
        twitter_summary = summarize_article(link)
        try:
            twitter_client.create_tweet(text=twitter_summary)
            save_digiato_sent_links([link])
            print("post_article")
        except Exception as e:
            print("Failed to post tweet:", e)

# === Rank and select the most relevant article based on keywords ===
def select_most_important_link(links):
    if not links:
        return None

    importance_keywords = {
        'new': 5, 'launch': 5, 'breakthrough': 4, 'review': 3, 'technology': 3,
        'smartphone': 3, 'ai': 3, 'update': 2, 'feature': 2
    }

    best_link = links[0]
    highest_score = 0

    for link in links:
        try:
            response = requests.get(link, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text().lower() if title_tag else extract_keywords_from_url(link).lower()

            score = sum(weight for keyword, weight in importance_keywords.items() if keyword in title or keyword in link.lower())
            score += (len(links) - links.index(link)) * 0.5  # Slight bias towards earlier articles

            if score > highest_score:
                highest_score = score
                best_link = link

        except Exception as e:
            print("Error scoring link:", e)
            continue

    return best_link

# === Generate and tweet Persian tech-related historical events with image ===
def send_calendar():
    timezone = pytz.timezone("Asia/Tehran")
    greg_today = datetime.datetime.now(timezone).date()
    weekday = greg_today.weekday()
    today = jdatetime.date.fromgregorian(date=greg_today)

    # Select the appropriate image based on the weekday
    # day_image_index = (weekday + 2) % len(day_images)  # Adjust index for correct day mapping
    # day_image = day_images[day_image_index]
    # day_image_path = os.path.abspath(day_image)

    # Check if the image file exists
    # if not os.path.exists(day_image_path):
    #     print(f"Error: Image file not found at {day_image_path}")
    #     return

    # Generate historical events prompt
    try:
        prompt = (f"write about three top historic events on day exactly {greg_today} for example if it is 2025-02-11 write about 02-11 in all years before write three short sentences in separate lines, focusing on technology, no politics or religion in Persian language")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
        events = response.choices[0].message.content.strip()
        print("Generated calendar events")
    except Exception as e:
        print(f"Calendar prompt failed: {e}")
        events = "رویدادهای تاریخی تکنولوژی در دسترس نیست."

    # Create tweet caption with events and hashtags
    twitter_caption = f"📅 امروز {today} ({greg_today})\n📌 {events}\n"
    hashtags = generate_hashtags(events)
    twitter_caption += ' '.join(hashtags) + '\n'

    # Upload image and post tweet
    try:
        # Upload image using Twitter v1.1 API
        # with open(day_image_path, 'rb') as image_file:
        #     media = twitter_api_v1.media_upload(filename=day_image, file=image_file)
        # media_id = media.media_id_string
        # print(f"Image uploaded successfully, media_id: {media_id}")

        # Post tweet with attached image using Twitter v2 API
        twitter_client.create_tweet(text=twitter_caption)
        print("Calendar tweet ")
    except Exception as e:
        print(f"Failed to send calendar tweet or upload image: {e}")
        # Fallback: Post tweet without image
        try:
            twitter_client.create_tweet(text=twitter_caption)
            print("Posted calendar tweet ")
        except Exception as fallback_e:
            print(f"Fallback tweet posting failed: {fallback_e}")

# === Schedule bot tasks ===
schedule.every().day.at("7:30").do(send_calendar)   # Post calendar once daily
schedule.every(30).minutes.do(post_article)  # Post news every 30 minutes


# === Main execution loop ===
def main():
    print("BOT Start")
    while True:
        schedule.run_pending()

# === Entry point ===
if __name__ == "__main__":
    main()
