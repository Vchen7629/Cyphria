import { ChevronUp, ExternalLink } from "lucide-react";
import type { Comment } from "../../mock/types";

interface TopCommentsProps {
  comments: Comment[];
}

const TopComments = ({ comments }: TopCommentsProps) => {
  if (comments.length === 0) return null;

  return (
    <div className="animate-fade-in-left">
      <section className="flex flex-col space-y-1 mb-3">
        <span className="text-sm text-orange-400 font-semibold">Top comments from Reddit</span>
        <span className="text-xs text-zinc-500">Most upvoted comments from Reddit</span>
      </section>
      <ul className="space-y-2">
        {comments.slice(0, 3).map((comment: Comment) => (
          <li key={comment.id} className="flex flex-col space-y-2 relative text-sm w-1/2 bg-zinc-800 px-3 py-1.5 rounded-lg text-zinc-400 leading-relaxed">
            <span className="text-zinc-400">"{comment.comment_text}"</span>
            <section className="flex relative items-center">
              <ChevronUp className="w-4 h-4 text-red-600"/>
              <span className="text-xs mr-2">{comment.score}</span>
              <span className="text-xs mr-2">10/25/2026</span>
              <a
                href={comment.reddit_link}
                target="_blank"
                rel="noopener noreferrer"
                className="absolute inline-flex items-center right-1.5 gap-1 text-xs text-orange-500 hover:text-zinc-400 transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                reddit
              </a>
            </section>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TopComments
