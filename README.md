Architecture:

<img width="365" alt="Screenshot 2024-10-21 at 5 46 42 PM" src="https://github.com/user-attachments/assets/0b4d66ee-5b3b-44f5-868b-f4166d427648">

Data processing: 
Here we have our code that interacts with the Reddit API and PRAW library. This part fetches posts from the specified subreddits, applying any filters such as hot or top posts, and retrieves metadata from those posts. We use HTML page title extraction to extract titles from HTML pages that are linked within the post bodies. This allows us to enhance the metadata being collected as it increases the searchability of the data being scrapped allowing for increased context on the data being scrapped. 

File System: 
For our crawler, we chose to use JSON files that hold all of the scraped data. Initially, our crawler uses a buffer to accumulate large amounts of scraped data before writing it to the disk. In our scenario when the buffer size reaches larger than 10MB the data is then serialized into a JSON file and written to the disk. Each JSON file follows a standardized naming convention as “file(file_counter).json where the file_counter increments with the creation of each new file. This allows for the sequential ordering of the files. This data is then stored in a JSON file that is located in the directory specified by the user during initial execution.

Error Handling/Rate Limiting: 
This part of the code contains error handling to deal with rate-limiting and Reddit API errors. When a rate limit is detected we use the sleep function which pauses the execution of the program for 60 seconds. Additionally, we also handle exceptions thrown from the Reddit API when we have issues fetching a subreddit or posts from that subreddit, where a general error message is printed when an unexpected response is received from the Reddit API. 

Data Collection Strategy:
	The crawling strategy of our Reddit crawler uses a list of subreddits from a text file along with an argument for posts per subreddit. Using the Python Reddit API wrapper (praw), we go through each specified subreddit and collect n top posts and n hot posts, then we store the post's title, body, ID, score, URL, permalink, type of post ("top" or "hot"), subreddit, comments, and hyperlinks into a buffer which is later written onto a file in a JSON format. We collect 10 comments per post.

Data Structures Employed:
The data structure employed is a list to store the crawled posts so far, which acts as a buffer before writing the data in a formatted way onto the destination file. This buffer only writes to disk when the buffer exceeds a specified length, in our case 10MB (if the max_size is smaller than 10MB, also save buffer to size when reach the max_size set).
We also utilize a hashmap in order to store what posts we have already read in order to avoid reading the same data twice. This both makes our crawler more efficient as well as make
	We use JSON objects to store posts with their metadata such as title, body, ID, score, URL, permalink, type of post ("top" or "hot"), subreddit, comments, and hyperlinks to maintain a seamless and flexible format for storing the scraped data. These JSON objects are then stored in JSON files that contain several serialized JSON objects. To ensure that duplicate posts are not being stored our system uses the scrapped_post_ids variable to uniquely identify each post to prevent redundancy in the scraped data. 

Limitations of the system:
	The crawler as of now cannot explore posts from subreddits that haven't already been specified in the text file.
	Due to our use of PRAW, we run into rate limitations from the Reddit API. These include rate limitations as well as API quota restrictions. Our implementation of using the sleep function does help mitigate these issues however it still greatly lowers our crawler's efficiency as it took nearly 7 hours to scrape 500MB of data. 
We found that using multithreading or asynchronous methods to gather the data was pointless as our API key will be rate limited at the same rate either way, since that was the main bottleneck for our program. 

Instructions to run the Crawler:
1. Make sure that Python and PRAW are installed on your system. 
2. Download the zip file containing the crawler and all necessary files and save it to your local directory. 
3. Create a text file such as “subreddits.txt” that includes the names of subreddits with each subreddit name being on a separate line, that you would like to be scrapped. 
4. Open the terminal/command prompt and from the directory where the code is located, execute the following command:
 ./crawler.sh subreddit_list.txt <max_posts>  <max_size>  <output_dir>

To recreate our requirements one might run the following:

./crawler.sh subreddit_list.txt 10 500000000 output_data
First, the executable for the crawler is being called with ./crawler.sh
The next argument is the text file (‘subreddits.txt’) which contains the list of subreddits you want to be scrapped. 
The next argument is the maximum number of posts to be scrapped, in this case 10 posts per subreddit.
The next argument is the maximum amount of data to be scrapped, in this case 500MB. 
The last argument is the directory where the output JSON file will be saved, here it’s “output_data”. 
