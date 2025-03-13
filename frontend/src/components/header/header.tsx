import { Bookmark, ChartSpline, Home, TextSearch, TrendingUp, User } from "lucide-react";
import { useLocation } from "react-router";

export function HeaderComponent() {
    const location = useLocation();
    
    const PageName = location.pathname.slice(1, 30)
    console.log(location.pathname)

    return (
        <header className="flex border-b-[1px] justify-between items-center border-bordercolor h-[10vh] w-[100%] px-[3vw]">
            <div className="flex items-center space-x-[2vw]">
                {PageName === "search" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <TextSearch />
                    </div>
                ) : PageName === "subredditstatistics" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <ChartSpline />
                    </div>
                ) : PageName === "bookmarks" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <Bookmark />
                    </div>
                ) : PageName === "userstatistics" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <User />
                    </div>
                ) : PageName === "trendingtopics" ? (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <TrendingUp />
                    </div>
                ) : (
                    <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                        <Home/>
                    </div>
                )}
                {PageName === "trendingtopics" ? (
                    <span className="text-xl font-bold">{"Trending Topics For Category"}</span>

                ) : PageName === "subredditstatistics" ? (
                    <span className="text-xl font-bold">{"Subreddit Statistics"}</span>

                ) : PageName === "userstatistics" ? (
                    <span className="text-xl font-bold">{"Your Statistics"}</span>
                ) : (
                    <span className="text-xl font-bold">{PageName || "Home"}</span>
                )}
            </div>
            <div className="flex space-x-3 items-center border-2 border-bordercolor bg-card py-1 px-2 rounded-xl">
                <div className="bg-gray-700 p-2 rounded-xl border-2 border-test2">
                    <User className="h-6 w-6"/>
                </div>
                <span className="text-md">Placeholder Username</span>
            </div>
        </header>
    )
}