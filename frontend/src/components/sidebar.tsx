import { TrendsButton } from "../navigation/sidebarbuttons.tsx/trendingtopicsbutton";
import { LogoutButton } from "../navigation/sidebarbuttons.tsx/logoutbutton";
import { SearchButton } from "../navigation/sidebarbuttons.tsx/searchbutton";
import { SubredditStatisticsButton } from "../navigation/sidebarbuttons.tsx/subredditstatsbutton";
import { BookmarkButton } from "../navigation/sidebarbuttons.tsx/bookmarkbutton";
import { LogoButton } from "../navigation/sidebarbuttons.tsx/logobutton";
import { UserStatisticsButton } from "../navigation/sidebarbuttons.tsx/userstatisticsbutton";

export function SidebarComponent() {

    return (
        <main className="left-0 flex flex-col items-center  w-[5vw] pt-[2vh]  h-[100vh] border-r-[1px] border-bordercolor">
            <LogoButton/>
            <div className="flex flex-col space-y-[4vh] mt-[5vh]">
                <SearchButton />
                <TrendsButton/>
                <SubredditStatisticsButton/>
                <UserStatisticsButton/>
                <BookmarkButton />
            </div>
            <div className="fixed flex flex-col bottom-[5vh] space-y-[3vh] items-center">
                <LogoutButton/>
            </div>
        </main>
    )
}