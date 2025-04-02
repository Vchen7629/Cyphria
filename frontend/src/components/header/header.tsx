import { Bookmark, ChartColumnStacked, ChartSpline, GitCompareArrowsIcon, Home, MessageSquareShare, User } from "lucide-react";
import { useSelector } from "react-redux";
import { useLocation } from "react-router";
import { selectCurrentUsername } from "../../app/state/authstate";

export function HeaderComponent() {
    const location = useLocation();
    const username = useSelector(selectCurrentUsername)
    
    const PageName = location.pathname.slice(1, 30)
    console.log(location.pathname)

    return (
        <header className="flex border-b-[1px] justify-between items-center border-bordercolor h-[10vh] py-[2vh] w-[100%] px-[3vw]">
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
            <div className="flex relative space-x-3 items-center border-2 max-w-[12%] border-bordercolor bg-card py-1 pl-2 pr-8 rounded-xl">
                <div className="bg-gray-700 p-2 rounded-xl border-2 border-test2">
                    <User className="h-6 w-6"/>
                </div>
                <span className=" text-md">{username || "Guest"}</span>
            </div>
        </header>
    )
}