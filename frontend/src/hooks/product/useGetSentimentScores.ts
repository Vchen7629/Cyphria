import { useQuery } from '@tanstack/react-query';
import { ProductMetadataService } from '../../api/services/product_metadata';
import { SentimentScoresResultProps } from '../../types/product';


interface SentimentScoresInputProps {
    product_name: string
    time_window: string
}

/**
 @hook

 @description - hook called when the user clicks the view more button on each product
 in the product topic page. Shows the sentiment scores (positive, neutral, negative)

 @param product_name - the product name we are fetching sentiment scores for
 @param time_window - the time window we are fetching  sentiment scores for

 @returns - the positive, neutral, and negative sentiment score counts
 */
export function useSearchProduct({ product_name, time_window }: SentimentScoresInputProps) {
    return useQuery<SentimentScoresResultProps>({
        queryKey: ['sentiment_score_product', product_name],
        queryFn: async () => {
            return await ProductMetadataService.sentiment_scores({ product_name, time_window });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}