import { Link } from "react-router";
import { ChevronRight } from "lucide-react";
import type { Topic } from "../../mock/types";

interface TopicCardProps {
  topic: Topic;
}

const TopicCard = ({ topic }: TopicCardProps) => {
  return (
    <Link
      to={`/${topic.parentSlug}/${topic.slug}`}
      className="group flex items-center justify-between p-4 rounded-lg border border-zinc-600/50 bg-zinc-800/30 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
    >
      <div>
        <h3 className="text-sm font-medium text-zinc-200 group-hover:text-zinc-100 transition-colors">
          {topic.name}
        </h3>
        <p className="text-xs text-zinc-500 mt-1">
          {topic.productCount} products ranked
        </p>
      </div>
      <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
    </Link>
  );
}

export default TopicCard