import { Layers2, MoonIcon } from "lucide-react";
import { HeaderComponent } from "../../../shared/components/header";
import { SidebarComponent } from "../../navigation/components/sidebar";
import { DatePickerWithRange } from "../../../shared/components/datefilter";
import { TopicSentimentsTimeChart } from "../../topic/components/sentiment-chart";
import { TopTopicsBarChart } from "../components/top-topics-bar-chart";
import { PostingFrequencyHeatMapChart } from "../components/posting-frequency-heatmap";
import { useSelector } from "react-redux";
import { selectExpandState } from "../../../app/state/ui";

export default function SubredditStatisticsPage() {
    const expand = useSelector(selectExpandState)

    return (
        <main className="flex  w-[100vw] h-[100vh] bg-background p-[1vw]">
            <SidebarComponent/>
            <div className={`flex flex-col ${expand ? "w-[87%] px-[4%]" : "w-[95vw] px-[3%]"} font-bold  overflow-auto`}>
                <HeaderComponent/>
                <section className="flex flex-col w-full">
                    <div className="relative flex items-center w-full h-[10vh] mt-[3vh]  space-x-[2vw]">
                        <div className="flex justify-center items-center">   
                            <Layers2 className="w-10 h-10"/>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-lg">Trends for "Subreddit"</span>
                            <span className="text-sm text-gray-400">Sentiment enhanced trends</span>
                        </div>
                        <div className="absolute right-0">
                           <DatePickerWithRange/> 
                        </div>
                    </div>
                    <div className="flex flex-col mt-[2vh]">
                        <div className="flex w-full items-center space-x-[2vw]">
                            <div className="bg-[#141414] w-[25vw] h-[40vh] pl-[1.5vw] pt-[1.5vh] rounded-2xl border-2 border-bordercolor">
                                <header className="w-full h-fit py-2">
                                    <span className="text-2xl font-thin text-gray-400">Trending Topics</span>
                                </header>
                            </div>
                            <TopTopicsBarChart/>
                        </div>                  
                    </div>
                    <div className="bg-[#141414] w-full mt-[5vh]">
                            <TopicSentimentsTimeChart/>
                    </div>
                    <div className="w-full w-full mt-[5vh]">
                        <PostingFrequencyHeatMapChart/>
                    </div>  
                    <a 
                        className="fixed flex justify-center items-center bottom-8 right-12 w-12 h-12 bg-card hover:bg-logo rounded-xl border-2 border-interactive"
                        href="/"
                    >
                        <MoonIcon/>
                    </a>
                </section>
            </div>
        </main>
    )
}