import { LogoButton } from "./logobutton";
import { ExpandButton } from "../../../shared/ui/buttons/expandbutton";
import { useSelector } from "react-redux";
import { selectExpandState } from "../../../app/state/ui";
import { CollapseButton } from "../../../shared/ui/buttons/collapseButton";
import NavButton from "./nav-button";
import { ChartColumnStacked, ChartSpline, GitCompareArrows, Home, MessageSquareShare } from "lucide-react";

export function SidebarComponent() {
    const expand = useSelector(selectExpandState)

    return (
        <main className={`left-0 flex flex-col rounded-xl bg-[#161617] ${expand ? "w-[13%] pl-[2vw]" : "w-[5vw] items-center"} pt-[2vh] border-bordercolor`}>
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
                <NavButton targetPage="/" label="home" buttonIcon={<Home/>}/>
                <NavButton targetPage="/comparison" label="Compare Topics" buttonIcon={<GitCompareArrows/>}/>
                <NavButton targetPage="/topic" label="Topic Trends" buttonIcon={<MessageSquareShare/>}/>
                <NavButton targetPage="/category" label="Category Trends" buttonIcon={<ChartColumnStacked/>}/>
                <NavButton targetPage="/subreddit" label="Subreddit Trends" buttonIcon={<ChartSpline/>}/>
            </div>
        </main>
    )
}