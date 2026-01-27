import { useQuery } from '@tanstack/react-query';
import { ProductCategoryService } from '../../api/services/product_category';

/**
 @hook

 @description - hook called when the user views the category page, fetches and displays
 the total number of products ranked for the category

 @param category - the category we are fetching total products count for

 @returns - the total products count count for that category
 */
export function useGetTotalProductsCount({ category }: { category: string }) {
    return useQuery<number>({
        queryKey: ['category_total_products', category],
        queryFn: async () => {
            return await ProductCategoryService.total_products_count({ category });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}