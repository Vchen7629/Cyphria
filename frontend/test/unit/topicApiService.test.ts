import { describe, it, expect, vi, beforeEach} from 'vitest'
import { ProductTopicService } from "../../src/api/services/product_topic"
import { insights_api } from "../../src/api/client/basePath"
import { mockRankedProductsListResponse, mockTotalOpinionsResponse, mockTotalProductsResponse } from '../mocks/topicEndpointResponse';

describe('TopicApiService', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    });

    // unit tests for total products ranked endpoint
    describe('total_products_ranked', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockTotalProductsResponse().number_products })

            const result = await ProductTopicService.total_products_ranked({product_topic: 'GPU'})

            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/topic/total_products_ranked?product_topic=GPU'
            )

            expect(result).toBe(10)
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductTopicService.total_products_ranked({product_topic: 'GPU'})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });

    // unit tests for total_opinions endpoint
    describe('total_opinions', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockTotalOpinionsResponse().number_opinions })

            const result = await ProductTopicService.total_opinions({
                product_topic: 'GPU',
                time_window: '7d'
            })

            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/topic/total_comments?product_topic=GPU&time_window=7d'
            )

            expect(result).toEqual(mockTotalOpinionsResponse().number_opinions)
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductTopicService.total_opinions({ product_topic: 'GPU', time_window: "7d"})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });

    // unit tests for ranked_products_list endpoint
    describe('ranked_products_list', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockRankedProductsListResponse().data })

            const result = await ProductTopicService.ranked_products_list({
                product_topic: 'GPU',
                time_window: '7d'
            })

            // should have called right endpoint with right params
            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/topic/products?product_topic=GPU&time_window=7d'
            );
            expect(insights_api.get).toHaveBeenCalledTimes(1)

            expect(result).toEqual(mockRankedProductsListResponse().data)
            expect(result[0].product_name).toBe('product_1')
            expect(result[1].product_name).toBe('product_2')
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductTopicService.ranked_products_list({ product_topic: 'GPU', time_window: '7d'})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });
})
