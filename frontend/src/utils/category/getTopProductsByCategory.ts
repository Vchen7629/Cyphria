import type { ProductV3 } from "../../mock/types";
import { mockProducts, getCategoryBySlug } from "../../mock/mockData";

export function getTopProductsByCategory(categorySlug: string, limit?: number): ProductV3[] | [] {
  const category = getCategoryBySlug(categorySlug);

  if (!category) {
    return [];
  }

  const allProducts: ProductV3[] = [];

  category.topics.forEach((topic) => {
    const topicProducts = mockProducts[topic.slug] || [];
    allProducts.push(...topicProducts);
  });

  const sortedProducts = allProducts.sort((a, b) => b.mention_count - a.mention_count);

  return limit ? sortedProducts.slice(0, limit) : sortedProducts;
}
