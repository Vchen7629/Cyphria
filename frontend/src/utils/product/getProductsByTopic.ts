import type { ProductV3 } from "../../mock/types";
import { mockProducts } from "../../mock/mockData";

export function getProductsByTopic(topicSlug: string): ProductV3[] {
  return mockProducts[topicSlug] || [];
}