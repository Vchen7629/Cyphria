import { Monitor } from "lucide-react";
import type { Topic } from "../../mock/types";
import iconMap from "../../utils/home/IconMap";
import { Link } from "react-router";

/**
  @component

  @description - List of  trending topics based on user searches on this website
  
  @param {Topic[]} topics- list of product topics
 */
const TrendingTopicsList = ({ topics }: { topics: Topic[] }) => {
  if (topics.length === 0) return null;

  return (
    <section>
      <h2 className="text-lg font-medium text-zinc-100">Trending Now</h2>
      <span className="text-sm font-light text-zinc-400">Most viewed product topics based on what other users are searching</span>
      <div className="flex space-x-2 mt-6">
        {topics.slice(0,6).map((topic) => {
          const IconComponent = iconMap[topic.icon] || Monitor;

          return (
            <Link
              to={`/${topic.parentSlug}/${topic.slug}`}
              className="w-1/6 items-center py-4 rounded-lg text-zinc-300 hover:text-zinc-400 border border-zinc-600/50 bg-zinc-700/20 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
            >
              <div className="flex flex-col items-center justify-center w-full">
                <div className="p-2 w-fit rounded-full bg-zinc-800/60">
                  <IconComponent className="w-5 h-5 text-zinc-400" />
                </div>
                <h4 className="text-sm max-w-[90%] font-semibold group-hover:text-zinc-100 truncate transition-colors">
                  {topic.name}
                </h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[12px] text-zinc-400">{topic.viewCount} Views</span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}

export default TrendingTopicsList
