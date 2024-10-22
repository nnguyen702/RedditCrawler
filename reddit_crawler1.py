import json
import praw
import os
import re
import sys
from urllib.parse import urlparse
from prawcore.exceptions import TooManyRequests, ResponseException
import time

if len(sys.argv) != 5:
    print("Usage: python reddit_crawler.py <subreddits_file.txt> <max_posts> <max_size> <output_dir>")
    sys.exit(1)

subreddits_file = sys.argv[1]
max_posts = int(sys.argv[2])
max_total_size = int(sys.argv[3])
output_dir = sys.argv[4]

reddit = praw.Reddit(
    client_id="your client id",
    client_secret="your client secrest",
    password="your password",
    user_agent="crapii by u/cs172_group17",
    username="cs172_group17",
)

# Load subreddits from file
with open(subreddits_file, 'r') as file:
    subreddits = [line.strip() for line in file.readlines()]

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Initialize file counter and buffer
file_counter = 1
buffer = []

# Initialize total_size
total_size = 0

# Set to store post IDs
scraped_post_ids = set()

def save_buffer_to_file(buffer, output_dir, file_counter):
    file_path = os.path.join(output_dir, f"file_{file_counter}.json")
    print(f"Saving buffer to json file {file_counter} in {output_dir}")
    with open(file_path, "w") as file:
        for post_data in buffer:
            json_str = json.dumps(post_data)
            file.write(json_str + "\n")
            global total_size
            total_size += len(json_str) + 1  # Add newline character size
    file_counter += 1
    buffer.clear()

def extract_hyperlinks(text):
    pattern = r'https?://\S+'
    hyperlinks = re.findall(pattern, text)
    return hyperlinks

for subreddit_name in subreddits:
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Crawling posts from subreddit: {subreddit_name}")
    except ResponseException as e:
        print(f"Error occurred while fetching subreddit '{subreddit_name}': {e}")
        continue

    try:
        top_posts = subreddit.top(limit=max_posts)
        hot_posts = subreddit.hot(limit=max_posts)

    except TooManyRequests:
        print("TooManyRequests exception occurred. Sleeping for 60 seconds.")
        time.sleep(60)
        continue
    except ResponseException as e:
        print(f"Error occurred while fetching posts from '{subreddit_name}': {e}")
        continue

    for post_list in [top_posts, hot_posts]:
        for post in post_list:
            if total_size >= max_total_size:
                print(f"Maximum total size of {max_total_size} bytes reached. Stopping scraping.")
                if buffer:
                    save_buffer_to_file(buffer, output_dir, file_counter)
                break

            if post.id in scraped_post_ids:
                continue

            hyperlinks = extract_hyperlinks(post.selftext)
            post_data = {
                'title': post.title,
                'body': post.selftext,
                'id': post.id,
                'score': post.score,
                'url': post.url,
                'permalink': post.permalink,
                'post_type': 'top' if post_list is top_posts else 'hot',
                'subreddit': subreddit_name,
                'comments': [],
                'hyperlinks': [urlparse(link).netloc for link in hyperlinks]
            }

            try:
                post.comments.replace_more(limit=10)
            except TooManyRequests:
                print("TooManyRequests exception occurred in post's comment. Sleeping for 60 seconds.")
                time.sleep(60)
                continue
            except ResponseException as e:
                print(f"Error occurred while fetching comments for post '{post.id}': {e}")
                continue

            for comment in post.comments.list():
                post_data['comments'].append({
                    'comment_id': comment.id,
                    'comment_body': comment.body,
                    'comment_score': comment.score
                })

            scraped_post_ids.add(post.id)
            buffer.append(post_data)
            buffer_size = sum(len(json.dumps(data)) for data in buffer)
            if  buffer_size>= max_total_size or buffer_size >= 10000000 : #10MB in bytes 
                save_buffer_to_file(buffer, output_dir, file_counter)

        if total_size >= max_total_size:
            break

    if total_size >= max_total_size:
        break

# Save remaining posts in buffer
if buffer:
    save_buffer_to_file(buffer, output_dir, file_counter)

