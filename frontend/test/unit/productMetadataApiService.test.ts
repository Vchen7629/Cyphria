import { describe, it, expect, vi, beforeEach} from 'vitest'
import { mockTopCommentsResponse, mockSearchResponse, mockSentimentScoresResponse } from "../mocks/productMetadataEndpointResponse";
import { ProductMetadataService } from "../../src/api/services/product_metadata"
import { insights_api } from "../../src/api/client/basePath"

describe('ProductMetadataApiService', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    });

    // unit tests for sentiment scores endpoint
    describe('sentiment_scores', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockSentimentScoresResponse().data })

            const result = await ProductMetadataService.sentiment_scores({
                product_name: 'iPhone',
                time_window: '7d'
            })

            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/product/sentiment_scores?product_name=iPhone&time_window=7d'
            )

            expect(result).toEqual(mockSentimentScoresResponse().data)
            expect(result.positive_sentiment_score).toBe(150)
            expect(result.neutral_sentiment_score).toBe(5)
            expect(result.negative_sentiment_score).toBe(2)
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductMetadataService.top_comments({ product_name: 'iPhone', time_window: "7d"})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });

    // unit tests for top_comments endpoint
    describe('top_comments', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockTopCommentsResponse().data })

            const result = await ProductMetadataService.top_comments({
                product_name: 'iPhone',
                time_window: '7d'
            })

            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/product/top_comments?product_name=iPhone&time_window=7d'
            )

            expect(result).toEqual(mockTopCommentsResponse().data)
            expect(result).toHaveLength(2)
            expect(result[0].score).toBe(150)
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductMetadataService.top_comments({ product_name: 'iPhone', time_window: "7d"})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });

    // unit tests for search_product endpoint
    describe('search_products', () => {
        it('should call the correct endpoint with query params', async() => {
            vi.mocked(insights_api.get).mockResolvedValueOnce({ data: mockSearchResponse().data })

            const result = await ProductMetadataService.search_products({
                query: 'iPhone',
                current_page: 1
            })

            // should have called right endpoint with right params
            expect(insights_api.get).toHaveBeenCalledWith(
                '/api/v1/product/search?q=iPhone&current_page=1'
            );
            expect(insights_api.get).toHaveBeenCalledTimes(1)

            expect(result).toEqual(mockSearchResponse().data)
            expect(result.products).toHaveLength(1)
            expect(result.current_page).toBe(1)
        });

        it('should handle errors and rethrow them', async () => {
            const mockError = new Error('Network error')
            vi.mocked(insights_api.get).mockRejectedValueOnce(mockError)

            await expect(
                ProductMetadataService.search_products({ query: 'test', current_page: 1})
            ).rejects.toThrow('Network error')

            expect(insights_api.get).toHaveBeenCalledTimes(1)
        });
    });
})
