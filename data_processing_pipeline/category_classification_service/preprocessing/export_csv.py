import csv, os

def exportCSV(body, subreddit):#, upvotes, downvotes, timestamp):
    header = [
        'body', 'subreddit', 'category',
    ]

    data = [
        body, subreddit, ''
    ]

    file_name = 'reddit-posts3.csv'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, '..', 'datasets')
    file_path = os.path.join(target_dir, file_name)
    file_exists = os.path.isfile(file_path)

    try: 
        os.makedirs(target_dir, exist_ok=True)
    except Exception as e:
        print(f"error with dir", e)
    else:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(data)