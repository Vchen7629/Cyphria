import { useQuery } from '@tanstack/react-query';
import { TopMentionedProductsResultProps } from '../../types/category';
import { ProductCategoryService } from '../../api/services/product_category';

/**
 @hook

 @description - hook called when the user visits the category page. Shows the top 6
 most mentioned products for the category

 @param category - the category we are fetching the top products for

 @returns - a list of the 6 top mentioned products objects
 */
export function useGetTopMentionedProducts({ category }: { category: string }) {
    return useQuery<TopMentionedProductsResultProps[]>({
        queryKey: ['category_top_mentioned_products', category],
        queryFn: async () => {
            return await ProductCategoryService.top_mentioned_products({ category });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}