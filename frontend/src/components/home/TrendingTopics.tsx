import type { Topic } from "../../mock/types";
import TrendingTopicCard from "./TrendingTopicCard";

export interface TopicComponentProps {
  topics: Topic[];
}

/**
  @component

  @description - Parent component for the trending topics based on user searches on this website
  
  @param {Topic[]} topics- list of product topics
 */
const TrendingTopics = ({ topics }: TopicComponentProps) => {
  if (topics.length === 0) return null;

  return (
    <section>
      <h2 className="text-lg font-medium text-zinc-100">Trending Now</h2>
      <span className="text-sm font-light text-zinc-400">Most viewed product topics based on what other users are searching</span>
      <div className="flex space-x-2 mt-6">
        {topics.map((topic) => (
          <TrendingTopicCard topic={topic} />
        ))}
      </div>
    </section>
  );
}

export default TrendingTopics
