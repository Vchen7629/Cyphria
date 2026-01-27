
import { AxiosError } from 'axios'
import { insights_api } from '../client/basePath'

/**
 @component

 @description - API call logic for homepage related data
 */
export const HomePageService = {
    // fetch the top 6 product topics by user view count across the site
    trending_product_topics: async() => {
        try {
            const response = await insights_api.get("/api/v1/home/trending/product_topics")
            
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