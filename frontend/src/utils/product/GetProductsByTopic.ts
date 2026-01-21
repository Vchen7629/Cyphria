import { mockProducts } from "../../mock/mockData";
import { ProductV3 } from "../../mock/types";

export function getProductsByTopic(topicSlug: string | undefined): ProductV3[] | [] {
    if (!topicSlug) return [];
    return mockProducts[topicSlug] || [];
}
