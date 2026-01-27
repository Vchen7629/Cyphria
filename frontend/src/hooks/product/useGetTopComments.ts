import { useQuery } from '@tanstack/react-query';
import { ProductMetadataService } from '../../api/services/product_metadata';
import { TopCommentsResultProps } from '../../types/product';


interface TopCommentsInputProps {
    product_name: string
    time_window: string
}

/**
 @hook

 @description - hook called when the user clicks the view more button on each product
 in the product topic page. Shows the top 5 reddit comments based on score for the product

 @param product_name - the product name we are fetching comments for
 @param time_window - the time_window we want to fetch comments for

 @returns a list of the top 5 reddit comments for the product and time window
 */
export function useGetTopComments({ product_name, time_window }: TopCommentsInputProps) {
    return useQuery<TopCommentsResultProps[]>({
        queryKey: ['product_top_comments', product_name],
        queryFn: async () => {
            return await ProductMetadataService.top_comments({ product_name, time_window });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}