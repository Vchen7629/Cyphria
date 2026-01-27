import { useQuery } from '@tanstack/react-query';
import { ProductTopicService } from '../../api/services/product_topic';

/**
 @hook

 @description - hook called when the user views the topic page, fetches and displays
 the total number of products ranked count for the topic

 @param product_topic - the product topic we are fetching total products ranked count for

 @returns - the total products ranked count for that topic
 */
export function useGetTotalProductsRanked({ product_topic }: { product_topic: string }) {
    return useQuery<number>({
        queryKey: ['topic_total_products_ranked', product_topic],
        queryFn: async () => {
            return await ProductTopicService.total_products_ranked({ product_topic });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}