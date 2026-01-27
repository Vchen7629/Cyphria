
import { AxiosError } from 'axios'
import { insights_api } from '../client/basePath'
import { RankedProductsListResultProps } from '../../types/topic'

interface RouteProps {
    product_topic: string
    time_window: string
}

/**
 @component

 @description - API call logic for product topic page related data
 */
export const ProductTopicService = {
    // fetch the amount of products ranked for the specified topic
    total_products_ranked: async({ product_topic }: { product_topic: string }): Promise<number> => {
        try {
            const response = await insights_api.get(`/api/v1/topic/total_products_ranked?product_topic=${product_topic}`)
            
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
    // fetch the amount of opinions (comments) for all products for the specified topic and time_window
    total_opinions: async({ product_topic, time_window }: RouteProps): Promise<number> => {
        try {
            const response = await insights_api.get(`/api/v1/topic/total_comments?product_topic=${product_topic}&time_window=${time_window}`)
        
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
    // fetch the list of ranked products organized by score to display on the product topic page
    ranked_products_list: async({ product_topic, time_window }: RouteProps): Promise<RankedProductsListResultProps[]> => {
        try {
            const response = await insights_api.get(`/api/v1/topic/products?product_topic=${product_topic}&time_window=${time_window}`)
        
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