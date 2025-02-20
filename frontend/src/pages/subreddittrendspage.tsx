import { Layers2 } from "lucide-react";
import { HeaderComponent } from "../components/header";
import { SidebarComponent } from "../components/sidebar";
import { DatePickerWithRange } from "../components/TopicTrendsPageComponents/datefilter";
import { TrendsTimeChart } from "../components/TopicTrendsPageComponents/timeserieschart";
import { TopTopicsBarChart } from "../components/SubredditTrendsPageComponents/toptopicsbarchart";
import { PostingFrequencyHeatMapChart } from "../components/SubredditTrendsPageComponents/postingfrequencyheatmap";

export default function SubredditStatisticsPage() {

    return (
        <main className="flex  w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <section className="flex flex-col w-full items-center font-bold">
                <HeaderComponent/>
                <section className="flex flex-col ml-[5vw] overflow-auto">
                    <div className="relative flex items-center w-[85vw] h-[10vh] mt-[1vh]  space-x-[2vw]">
                        <div className="flex justify-center items-center">   
                            <Layers2 className="w-10 h-10"/>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-lg">Trends for "Subreddit"</span>
                            <span className="text-sm text-gray-400">Sentiment enhanced trends</span>
                        </div>
                        <div className="absolute right-[6vw]">
                           <DatePickerWithRange/> 
                        </div>
                    </div>
                    <div className="flex mt-[2vh] space-x-[2vw]">
                        <div>
                            <div className="flex w-full items-center space-x-[2vw]">
                                <div className="bg-[#141414] w-[25vw] h-[40vh] pl-[1.5vw] pt-[1.5vh] rounded-2xl border-2 border-bordercolor">
                                    <header className="w-full h-fit py-2">
                                        <span className="text-2xl font-thin text-gray-400">Trending Topics</span>
                                    </header>
                                </div>
                                <TopTopicsBarChart/>
                            </div>
                            <div className="bg-[#141414] w-[52vw] mt-[5vh]">
                                <TrendsTimeChart/>
                            </div>
                        </div>
                        <PostingFrequencyHeatMapChart/>
                    </div>
                </section>
            </section>
        </main>
    )
}