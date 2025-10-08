import { Bookmark, ChartColumnStacked, ChartSpline, GitCompareArrowsIcon, Home, MessageSquareShare, User } from "lucide-react";
import { useLocation } from "react-router";

export function HeaderComponent() {
    const location = useLocation();    
    const PageName = location.pathname.slice(1, 30)

    return (
        <header className="flex border-b-[1px] justify-between items-center border-bordercolor h-[10vh] py-[2vh] w-full">
            <div className="flex items-center space-x-[2vw]">
                {PageName === "comparison" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <GitCompareArrowsIcon/>
                    </div>
                ) : PageName === "topic" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <MessageSquareShare />
                    </div>
                ) : PageName === "subreddit" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <ChartSpline />
                    </div>
                ) : PageName === "bookmarks" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <Bookmark />
                    </div>
                ) : PageName === "user" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <User />
                    </div>
                ) : PageName === "category" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <ChartColumnStacked />
                    </div>
                ) : (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <Home/>
                    </div>
                )}
                {PageName === "comparison" ? (
                    <span className="text-xl font-bold">{"Sentiment enhanced Comparison for topics"}</span>
                ) : PageName === "topic" ? (
                    <span className="text-xl font-bold">{"Topic Sentiments and Trends"}</span>
                ) : PageName === "category" ? (
                    <span className="text-xl font-bold">{"Category Sentiments and Trends"}</span>
                ) : PageName === "subreddit" ? (
                    <span className="text-xl font-bold">{"Subreddit Sentiments and Trends"}</span>

                ) : PageName === "user" ? (
                    <span className="text-xl font-bold">{"Your Statistics"}</span>
                ) : (
                    <span className="text-xl font-bold">{PageName || "Home"}</span>
                )}
            </div>
        </header>
    )
}