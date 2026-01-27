import { useQuery } from '@tanstack/react-query';
import { ProductMetadataService } from '../../api/services/product_metadata';
import { SearchResultProps } from '../../types/product';


interface SearchInputProps {
    query: string
    current_page: number
}

/**
 @hook

 @description - hook used by the searchbar in the header to call the insights api and
 fetch the list of matching products

 @param query - the product name we are searching for
 @param current_page - the current page of the search bar dropdown list, used for
 pagination

 @returns a dictionary containing, a list of up to 6 matching products
 the current page number of pagination, and the total pages of pagination
 */
export function useSearchProduct({ query, current_page }: SearchInputProps) {
    return useQuery<SearchResultProps>({
        queryKey: ['query', query],
        queryFn: async () => {
            return await ProductMetadataService.search_products({ query, current_page });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}