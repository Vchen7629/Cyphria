import { CategoryTrendsButton } from "../navigation/sidebarbuttons.tsx/categorytrendsbutton";
import { LogoutButton } from "../navigation/sidebarbuttons.tsx/logoutbutton";
import { TopicButton } from "../navigation/sidebarbuttons.tsx/topictrendsbutton";
import { SubredditStatisticsButton } from "../navigation/sidebarbuttons.tsx/subredditstatsbutton";
import { BookmarkButton } from "../navigation/sidebarbuttons.tsx/bookmarkbutton";
import { LogoButton } from "../navigation/sidebarbuttons.tsx/logobutton";
import { UserStatisticsButton } from "../navigation/sidebarbuttons.tsx/userstatisticsbutton";
import { LoginButton } from "../navigation/sidebarbuttons.tsx/loginbutton";
import { ComparisonButton } from "../navigation/sidebarbuttons.tsx/comparisonbutton";
import { useState } from "react";

export function SidebarComponent() {
    const [expand, setExpand] = useState<boolean>(true)

    function ToggleExpand() {
        setExpand(false)
    }
    return (
        <main className={`left-0 flex flex-col ${expand ? "w-[15vw] pl-[2vw]" : "w-[5vw] items-center"} pt-[2vh]  h-[100vh] border-r-[1px] border-bordercolor`}>
            <LogoButton expand={expand}/>
            <div className="flex flex-col space-y-[4vh] mt-[5vh]">
                <ComparisonButton expand={expand}/>
                <TopicButton expand={expand}/>
                <CategoryTrendsButton expand={expand}/>
                <SubredditStatisticsButton expand={expand}/>
                <UserStatisticsButton expand={expand}/>
                <BookmarkButton expand={expand}/>
            </div>
            <div className="fixed flex flex-col bottom-[5vh] space-y-[3vh] items-center">
                <LoginButton expand={expand}/>
                <LogoutButton expand={expand}/>
            </div>
        </main>
    )
}