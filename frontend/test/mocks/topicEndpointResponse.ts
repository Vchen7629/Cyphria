/**
 @component

 @description - factory function mocking the total products ranked endpoint response data
 */
export const mockTotalProductsResponse = () => ({
    number_products: 10
})

/**
 @component

 @description - factory function mocking the total opinions endpoint response data
 */
export const mockTotalOpinionsResponse = () => ({
    number_opinions: 500
})

/**
 @component

 @description - factory function mocking the ranked_products_list endpoint response data
 */
export const mockRankedProductsListResponse = () => ({
    data: [
        {
            product_name: "product_1",
            grade: "S",
            bayesian_score: 97,
            mention_count: 100,
            approval_percentage: 87,
            is_top_pick: true,
            is_most_discussed: false,
            has_limited_data: false
        },
        {
            product_name: "product_2",
            grade: "A",
            bayesian_score: 86,
            mention_count: 250,
            approval_percentage: 60,
            is_top_pick: false,
            is_most_discussed: true,
            has_limited_data: false
        }
    ]
})