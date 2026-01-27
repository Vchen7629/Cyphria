export interface RankedProductsListResultProps {
    product_name: string
    grade: string
    bayesian_score: number
    mention_count: number
    approval_percentage: number
    is_top_pick: boolean
    is_most_discussed: boolean
    has_limited_data: boolean
}