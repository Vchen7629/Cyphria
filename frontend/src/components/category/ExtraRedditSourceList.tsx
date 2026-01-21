import { ChevronDown } from "lucide-react";
import { Subreddit } from "../../mock/types";
import { useState } from "react";

interface ExtraRedditSourceProps {
    subreddits: Subreddit[]
    totalExtra: number
}

const ExtraRedditSourceList = ({ subreddits, totalExtra }: ExtraRedditSourceProps) => {
    const [showList, setShowList] = useState<boolean>(false)

    return (
        <div className="relative">
            <button 
                onClick={() => setShowList(prev => !prev)}
                className="flex items-center py-1 px-3 bg-zinc-700 rounded-lg text-zinc-200 border border-zinc-600 hover:bg-zinc-800 hover:border-zinc-700 transition-colors duration-250"
            >
                <span className="flex items-center text-xs">
                    +{totalExtra} more <ChevronDown size={14} className={`ml-1 mt-0.5 transition-transform duration-250 ${showList ? "rotate-180" : ""}`}/>
                </span>
            </button>
            {showList && (
                <ul className="flex flex-col space-y-2 absolute w-[140%] max-h-30 overflow-auto mt-2 left-[-20%] py-2 px-2 bg-zinc-800 rounded-lg text-zinc-400 z-50">
                    <span className="text-xs ml-2">+{totalExtra} extra sources</span>
                    {subreddits.map((subreddit: Subreddit) => (
                        <a
                            href={`https://www.reddit.com/r/${subreddit.name}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center py-1 px-3 bg-orange-600 rounded-lg text-white border border-orange-700 hover:text-zinc-200 hover:border-orange-400 transition-colors duration-250"
                        >
                            <span className="text-xs truncate">r/{subreddit.name}</span>
                        </a>
                    ))}
                </ul>
            )}
        </div>
    )
}

export default ExtraRedditSourceList