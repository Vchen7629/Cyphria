/**
 @component

 @description - factory function mocking the sentiment_scores result endpoint response data
 */
export const mockSentimentScoresResponse = () => ({
    data: {
        positive_sentiment_score: 150,
        neutral_sentiment_score: 5,
        negative_sentiment_score: 2
    }
})

/**
 @component

 @description - factory function mocking the top_comments result endpoint response data
 */
export const mockTopCommentsResponse = () => ({
    data: [
        {
            comment_text: 'product 1 is good',
            reddit_link: 'https://reddit.com/r/test/123',
            score: 150,
            created_utc: '2024-01-01T00:00:00Z'
        },
        {
            comment_text: 'product 2 is better',
            reddit_link: 'https://reddit.com/r/test/456',
            score: 300,
            created_utc: '2024-01-02T00:00:00Z'
        }
    ]
})

/**
 @component

 @description - factory function mocking the search result endpoint response data
 */
export const mockSearchResponse = () => ({
    data: {
        products: [
            { product_name: "iPhone", product_topic: "tech", grade: "A", mention_count: 100 }
        ],
        current_page: 1,
        total_pages: 5
    }
})