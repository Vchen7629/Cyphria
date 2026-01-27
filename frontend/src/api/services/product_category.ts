
import { AxiosError } from 'axios'
import { insights_api } from '../client/basePath'
import { TopMentionedProductForTopicResultProps, TopMentionedProductsResultProps } from '../../types/category'

/**
 @component

 @description - API call logic for product category page related data
 */
export const ProductCategoryService = {
    // fetch the top 3 products by mention count for the category
    top_mentioned_products: async({ category }: { category: string }): Promise<TopMentionedProductsResultProps[]> => {
        try {
            const response = await insights_api.get(`/api/v1/category/top_mentioned_products?category=${category}`)
            
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
    // fetch the amount of products for the specified category
    total_products_count: async({ category }: { category: string }): Promise<number> => {
        try {
            const response = await insights_api.get(`/api/v1/category/total_products_count?category=${category}`)
        
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
    // fetch the top 3 products based on mention count for the individual product topic cards on category page
    top_mentioned_product_for_topic: async({ product_topic }: { product_topic: string }): Promise<TopMentionedProductForTopicResultProps[]> => {
        try {
            const response = await insights_api.get(`/api/v1/category/topic_most_mentioned_product?product_topic=${product_topic}`)
        
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