import { ExternalLink } from "lucide-react";
import type { Comment } from "../../mock/types";

interface TopCommentsProps {
  comments: Comment[];
}

const TopComments = ({ comments }: TopCommentsProps) => {
  if (comments.length === 0) return null;

  return (
    <div className="space-y-3">
      <span className="text-xs text-zinc-500 font-medium">Top comments from Reddit</span>
      <ul className="space-y-2">
        {comments.slice(0, 3).map((c) => (
          <li key={c.id} className="text-sm text-zinc-400 leading-relaxed">
            <span className="text-zinc-500">"</span>
            {c.comment_text}
            <span className="text-zinc-500">"</span>
            <a
              href={c.reddit_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 ml-2 text-xs text-zinc-600 hover:text-zinc-400 transition-colors"
            >
              <ExternalLink className="w-3 h-3" />
              reddit
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TopComments
