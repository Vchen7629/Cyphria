import { ChevronDown, ChevronRight } from "lucide-react";
import { Subreddit } from "../../mock/types";
import { useState } from "react";
import RedditSourcePill from "./RedditSourcePill";

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
                className="flex items-center py-1 px-3 bg-orange-400 rounded-lg text-zinc-200 border border-orange-600 hover:bg-orange-500 hover:border-orange-400 transition-colors duration-250"
            >
                <span className="flex items-center text-xs">
                +{totalExtra} more <ChevronDown size={14} className="ml-1 mt-0.5"/>
                </span>
            </button>
            {showList && (
                <ul className="flex flex-col space-y-2 absolute w-[140%] max-h-30 overflow-auto mt-2 left-[-20%] py-2 px-2 bg-zinc-800 rounded-lg text-zinc-400">
                    <span className="text-xs ml-2">+{totalExtra} extra sources</span>
                    {subreddits.map((subreddit: Subreddit) => (
                        <RedditSourcePill subreddit={subreddit}/>
                    ))}
                </ul>
            )}
        </div>
    )
}

export default ExtraRedditSourceList