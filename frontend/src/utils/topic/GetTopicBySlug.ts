import type { Topic, Category } from "../../mock/types";
import { mockCategories } from "../../mock/mockData";

export function getTopicBySlug(parentSlug: string, topicSlug: string): { parent: Category; topic: Topic } | undefined {
  const parent = mockCategories.find(cat => cat.slug === parentSlug);
  if (!parent) return undefined;
  const topic = parent.topics.find(sub => sub.slug === topicSlug);
  if (!topic) return undefined;
  return { parent, topic };
}
