import { ChartButton } from "../../navigation/sidebarbuttons.tsx/chartbutton";
import { LogoutButton } from "../../navigation/sidebarbuttons.tsx/logoutbutton";
import { UserButton } from "../../navigation/sidebarbuttons.tsx/userbutton";
import Logo from "../../assets/logo.svg"
import { SearchButton } from "../../navigation/sidebarbuttons.tsx/searchbutton";
import { TemporalAnalysisButton } from "../../navigation/sidebarbuttons.tsx/temporalanalysis";
import { BookmarkButton } from "../../navigation/sidebarbuttons.tsx/bookmarkbutton";

export function SidebarComponent() {

    return (
        <main className="left-0 flex flex-col items-center  w-[5vw] pt-[2vh]  h-[100vh] border-r-[1px] border-bordercolor">
            <img src={Logo} alt="Logo" className="w-12 h-12 mb-[5vh]" />
            <div className="flex flex-col space-y-[4vh]">
                <SearchButton />
                <TemporalAnalysisButton />
                <ChartButton/>
                <BookmarkButton />
            </div>
            <div className="fixed flex flex-col bottom-[5vh] space-y-[3vh] items-center">
                <UserButton />
                <LogoutButton/>
            </div>
        </main>
    )
}