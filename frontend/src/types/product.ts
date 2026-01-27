
export interface SearchResultProps {
    products?: {
        product_name: string
        product_topic: string
        grade: string
        mention_count: number
    }[]
    current_page: number
    total_pages: number
}

export interface TopCommentsResultProps {
    comment_text: string
    reddit_link: string
    score: number
    created_utc: string
}

export interface SentimentScoresResultProps {
    positive_sentiment_score: number
    neutral_sentiment_score: number
    negative_sentiment_score: number
}