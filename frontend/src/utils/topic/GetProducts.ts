import { ProductV3 } from "../../mock/types";
import { getProductsByTopic } from "../product/getProductsByTopic";

export function getProducts(topic: any): ProductV3[] {
    if (!topic) return [];
    return getProductsByTopic(topic);
}
