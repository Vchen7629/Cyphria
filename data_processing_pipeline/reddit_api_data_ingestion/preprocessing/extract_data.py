def relevantData(apiRes):
    if 'data' in apiRes:
        post_data = apiRes['data']
    else:
        post_data = apiRes
        
    body = post_data.get('title', '') + " " + post_data.get('selftext', '')
    subreddit = post_data.get('subreddit', '')
    upvotes = post_data.get('ups', '')
    downvotes = post_data.get('downs', '')
    #post_id = post_data.get('id', '')
    created_utc = post_data.get('created_utc', '')
        
    return body, subreddit, upvotes, downvotes, created_utc
    
    

