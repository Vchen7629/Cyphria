/**
 @component

 @description - factory function mocking the top_mentioned_products endpoint response data
 */
export const mockTopMentionedProductsResponse = () => ({
    data: [
        {
            product_name: "product_1",
            grade: "S",
            mention_count: 100,
            topic_name: "GPU"
        },
        {
            product_name: "product_2",
            grade: "A+",
            mention_count: 95,
            topic_name: "GPU"
        },
        {
            product_name: "product_3",
            grade: "A",
            mention_count: 90,
            topic_name: "GPU"
        },
        {
            product_name: "product_4",
            grade: "B+",
            mention_count: 90,
            topic_name: "GPU"
        },
        {
            product_name: "product_5",
            grade: "B",
            mention_count: 85,
            topic_name: "GPU"
        },
        {
            product_name: "product_6",
            grade: "C+",
            mention_count: 80,
            topic_name: "GPU"
        },
    ]
})

/**
 @component

 @description - factory function mocking the total_products_count endpoint response data
 */
export const mockTotalProductsCountResponse = () => ({
    product_count: 22
})

/**
 @component

 @description - factory function mocking the top_mentioned_product_for_topic endpoint response data
 */
export const mockTopMentionedProductForTopicResponse = () => ({
    data: [
        {
            product_name: "product_1",
            grade: "S",
        },
        {
            product_name: "product_2",
            grade: "A",
        },
        {
            product_name: "product_3",
            grade: "B",
        }
    ]
})