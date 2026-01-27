
import { AxiosError } from 'axios'
import { insights_api } from '../client/basePath'

interface ProductProps {
    product_name: string
    time_window: string
}

interface SearchProps {
    query: string,
    current_page: number
}

/**
 @component

 @description - API call logic for product specific related data
 */
export const ProductMetadataService = {
    // fetch the positive, neutral, negative sentiment score amount for specified product and time window
    sentiment_scores: async({ product_name, time_window }: ProductProps) => {
        try {
            const response = await insights_api.get(`/api/v1/product/sentiment_scores?product_name=${product_name}&time_window=${time_window}`)
            
            return response.data
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error(error.response?.data || error.message);
                throw error;
            } else if (error instanceof Error) {
                console.error(error.message);
                throw error;
            } else {
                console.error(error);
                throw error;
            }
        }
    },
    // fetch the top 5 comments based on reddit score for the specified product and time window
    top_comments: async({ product_name, time_window }: ProductProps) => {
        try {
            const response = await insights_api.get(`/api/v1/product/top_comments?product_name=${product_name}&time_window=${time_window}`)
        
            return response.data
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error(error.response?.data || error.message);
                throw error;
            } else if (error instanceof Error) {
                console.error(error.message);
                throw error;
            } else {
                console.error(error);
                throw error;
            }
        }
    },
    // fetch a list of products matching the search query
    search_products: async({ query, current_page }: SearchProps) => {
        try {
            const response = await insights_api.get(`/api/v1/product/search?q=${query}&current_page=${current_page}`)
        
            return response.data
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error(error.response?.data || error.message);
                throw error;
            } else if (error instanceof Error) {
                console.error(error.message);
                throw error;
            } else {
                console.error(error);
                throw error;
            }
        }
    }
}   