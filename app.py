from bs4 import BeautifulSoup
from selenium import webdriver
import time
import schedule
import threading

def scrape_youtube_videos():
    # Initialize the WebDriver
    driver = webdriver.Chrome()

    # Open the YouTube channel URL
    driver.get("youtube_url(channel)")

    # Scroll down to load more videos
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Wait for all video elements to load
    time.sleep(5)

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all video links and titles using the appropriate selectors
    video_data = []
    for a in soup.select('a#thumbnail'):
        href = a.get('href')
        if href and 'watch' in href:
            title = a.find_next('h3').text.strip() if a.find_next('h3') else 'No title found'
            video_data.append({'link': 'https://www.youtube.com' + href, 'title': title})

    # Close the WebDriver
    driver.quit()

    # Debug print to check the links and titles
    print("Videos found:")
    for video in video_data:
        print(f"Title: {video['title']}, Link: {video['link']}")

    # Save the video links and titles to a text file
    with open('video_data.txt', 'w') as f:
        for video in video_data:
            f.write(f"Title: {video['title']}, Link: {video['link']}\n")

    print(f"Saved {len(video_data)} videos to video_data.txt")

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

# Schedule the scraping function to run every 24 hours
schedule.every(24).hours.do(scrape_youtube_videos)

# Start the continuous scheduling
cease_run = run_continuously()

# Keep the script running
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    # Stop the continuous run loop
    cease_run.set()
