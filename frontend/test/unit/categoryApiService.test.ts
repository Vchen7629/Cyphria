import { describe, it, expect, vi, beforeEach} from 'vitest'
import { ProductCategoryService } from "../../src/api/services/product_category"
import { insights_api } from "../../src/api/client/basePath"
import { mockTopMentionedProductForTopicResponse, mockTopMentionedProductsResponse, mockTotalProductsCountResponse } from '../mocks/categoryEndpointResponse';

describe('CategoryApiService', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    });

    // unit tests for top_mentioned_products endpoint
    describe('top_mentioned_products', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockTopMentionedProductsResponse().data })

            const result = await ProductCategoryService.top_mentioned_products({category: 'Computing'})

            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/category/top_mentioned_products?category=Computing'
            )

            expect(result).toEqual(mockTopMentionedProductsResponse().data)
            expect(result).length(6)
            expect(result[0].product_name).toBe("product_1")
            expect(result[1].product_name).toBe("product_2")
            expect(result[2].product_name).toBe("product_3")
            expect(result[3].product_name).toBe("product_4")
            expect(result[4].product_name).toBe("product_5")
            expect(result[5].product_name).toBe("product_6")
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductCategoryService.top_mentioned_products({category: 'Computing'})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });

    // unit tests for total_products_count endpoint
    describe('total_products_count', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockTotalProductsCountResponse().product_count })

            const result = await ProductCategoryService.total_products_count({ category: "Computing" })
 
            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/category/total_products_count?category=Computing'
            )

            expect(result).toEqual(22)
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductCategoryService.total_products_count({ category: 'Computing' })
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });

    // unit tests for top_mentioned_product_for_topic endpoint
    describe('top_mentioned_product_for_topic', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockTopMentionedProductForTopicResponse().data })

            const result = await ProductCategoryService.top_mentioned_product_for_topic({ product_topic: 'GPU' })

            // should have called right endpoint with right params
            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/category/topic_most_mentioned_product?product_topic=GPU'
            );
            expect(insights_api.get).toHaveBeenCalledTimes(1)

            expect(result).toEqual(mockTopMentionedProductForTopicResponse().data)
            expect(result[0].product_name).toBe('product_1')
            expect(result[1].product_name).toBe('product_2')
            expect(result[2].product_name).toBe('product_3')
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductCategoryService.top_mentioned_product_for_topic({ product_topic: 'GPU' })
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });
})
