import { CategoryTrendsButton } from "../navigation/sidebarbuttons.tsx/categorytrendsbutton";
import { LogoutButton } from "../navigation/sidebarbuttons.tsx/logoutbutton";
import { TopicButton } from "../navigation/sidebarbuttons.tsx/topictrendsbutton";
import { SubredditStatisticsButton } from "../navigation/sidebarbuttons.tsx/subredditstatsbutton";
import { BookmarkButton } from "../navigation/sidebarbuttons.tsx/bookmarkbutton";
import { LogoButton } from "../navigation/sidebarbuttons.tsx/logobutton";
import { UserStatisticsButton } from "../navigation/sidebarbuttons.tsx/userstatisticsbutton";
import { LoginButton } from "../navigation/sidebarbuttons.tsx/loginbutton";
import { ComparisonButton } from "../navigation/sidebarbuttons.tsx/comparisonbutton";
import { ExpandButton } from "../ui/buttons/expandbutton";
import { useSelector } from "react-redux";
import { selectExpandState } from "../app/stateSlices/expandSlice";
import { CollapseButton } from "../ui/buttons/collapseButton";

export function SidebarComponent() {
    const expand = useSelector(selectExpandState)

    return (
        <main className={`left-0 flex flex-col ${expand ? "w-[15vw] pl-[2vw]" : "w-[5vw] items-center"} pt-[2vh]  h-[100vh] border-r-[1px] border-bordercolor`}>
            {expand ? (
                <div className="flex justify-between pr-[1.5vw]">
                    <LogoButton/>
                    <ExpandButton/>
                </div>
            ) : (
                <div className="flex flex-col justify-center items-center">
                    <LogoButton/>
                    <CollapseButton/>
                </div>
            )}            
            <div className="flex flex-col space-y-[4vh] mt-[5vh]">
                <ComparisonButton/>
                <TopicButton/>
                <CategoryTrendsButton/>
                <SubredditStatisticsButton/>
                <UserStatisticsButton/>
                <BookmarkButton/>
            </div>
            <div className="fixed flex flex-col bottom-[5vh] space-y-[3vh] items-center">
                <LoginButton/>
                <LogoutButton/>
            </div>
        </main>
    )
}