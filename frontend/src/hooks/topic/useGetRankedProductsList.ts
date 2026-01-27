import { useQuery } from '@tanstack/react-query';
import { ProductTopicService } from '../../api/services/product_topic';
import { RankedProductsListResultProps } from '../../types/topic';


interface RankedProductsListProps {
    product_topic: string
    time_window: string
}

/**
 @hook

 @description - hook called when the user visits a topic page. Fetches the list of products ranked by
 score from the insights api for the topic and time_window

 @param product_topic - the product topic we are fetching ranked list of products for
 @param time_window - the time_window we want to fetch ranked list of products for

 @returns a list of products ranked by their score for the specified topic and time window
 */
export function useGetRankedProductsList({ product_topic, time_window }: RankedProductsListProps) {
    return useQuery<RankedProductsListResultProps[]>({
        queryKey: ['topic_ranked_products_list', product_topic],
        queryFn: async () => {
            return await ProductTopicService.ranked_products_list({ product_topic, time_window });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}