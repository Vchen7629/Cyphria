import { Subreddit } from "../../mock/types"

const RedditSourcePill = ({ subreddit }: {subreddit: Subreddit}) => {

    return (
        <a
            href={`https://www.reddit.com/r/${subreddit.name}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center py-1 px-3 bg-orange-600 rounded-lg text-white border border-orange-700 hover:text-zinc-200 hover:border-orange-400 transition-colors duration-250"
        >
            <span className="text-xs truncate">r/{subreddit.name}</span>
        </a>
    )
}

export default RedditSourcePill