import { useQuery } from '@tanstack/react-query';
import { ProductCategoryService } from '../../api/services/product_category';
import { TopMentionedProductForTopicResultProps } from '../../types/category';

/**
 @hook

 @description - hook called and used by the individual topic cards on the category page.
 fetches and displays the top 3 products based on mention count for each topic

 @param product_topic - the product_topic we are fetching top 3 products for

 @returns - a list of the top 3 products for the topic, each item containing name and grade
 */
export function useGetTopMentionedProductForTopic({ product_topic }: { product_topic: string }) {
    return useQuery<TopMentionedProductForTopicResultProps[]>({
        queryKey: ['category_topic_top_mentioned_products', product_topic],
        queryFn: async () => {
            return await ProductCategoryService.top_mentioned_product_for_topic({ product_topic });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}