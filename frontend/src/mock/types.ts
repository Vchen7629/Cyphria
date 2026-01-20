export type Grade = "S" | "A+" | "A" | "A-" | "B+" | "B" | "B-" | "C+" | "C" | "C-" | "D+" | "D" | "D-" | "F";

export type TimeWindow = "90d" | "all";

export type FilterType = "best" | "discussed" | "approval" | "hidden_gems";

export interface Category {
  id: string;
  name: string;
  slug: string;
  icon: string;
  guideCount: number;
  viewCount: number;
  topics: Topic[];
}

export interface Topic {
  id: string;
  name: string;
  slug: string;
  icon: string;
  parentSlug: string;
  productCount: number;
  viewCount?: number;
}

export interface ProductV3 {
  id: string;
  product_name: string;
  rank: number;
  grade: Grade;
  mention_count: number;
  approval_percentage: number;
  is_top_pick: boolean;
  is_most_discussed: boolean;
  is_hidden_gem: boolean;
  has_limited_data: boolean;
  tldr_summary: string;
  parentSlug: string;
  subcategory_slug: string;
}

export interface Sentiment {
  positive_count: number;
  neutral_count: number;
  negative_count: number;
}

export interface Comment {
  id: string;
  comment_text: string;
  reddit_link: string;
  score: number;
}

export interface TrendingCategory {
  id: string;
  product_name: string;
  category: string;
  subcategory: string;
  grade: Grade;
  trendReason: string;
}
