import { MessageSquareMore, MoonIcon } from "lucide-react";
import { HeaderComponent } from "../components/header/header";
import { SidebarComponent } from "../components/sidebar";
import { DatePickerWithRange } from "../components/TopicTrendsPageComponents/datefilter";
import { TopicSentimentsTimeChart } from "../components/TopicTrendsPageComponents/TopicSentimentsChart";
import { useSelector } from "react-redux";
import { selectExpandState } from "../app/stateSlices/expandSlice";
import { TopSubredditAppearancesChart } from "../components/TopicTrendsPageComponents/topSubredditChart";
import { EngagementMetricsChart } from "../components/TopicTrendsPageComponents/EngagementMetricsChart";
import { PostingFrequencyChart } from "../components/TopicTrendsPageComponents/PostingFrequencyOverTimeChart";
import { EmotionsSentimentChart } from "../components/TopicTrendsPageComponents/EmotionsSentimentChart";

export default function SearchPage() {
    const expand = useSelector(selectExpandState)
    
    return (
        <main className="flex w-[100vw] h-[100vh] bg-background p-[1vw]">
            <SidebarComponent/>
            <div className={`flex flex-col ${expand ? "w-[87%] px-[4%]" : "w-[95vw] px-[3%]"} font-bold  overflow-auto`}>
                <HeaderComponent/>
                <section className="flex flex-col w-full">
                    <div className="relative flex items-center w-full h-[10vh] my-[3vh]  space-x-[2vw]">
                        <div className="flex justify-center items-center">   
                            <MessageSquareMore className="w-10 h-10"/>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-lg">Trends for "Topic"</span>
                            <span className="text-sm text-gray-400">Sentiment enhanced Trends</span>
                        </div>
                        <div className="absolute right-0">
                           <DatePickerWithRange/> 
                        </div>
                    </div>
                    <div className="flex space-x-[2vw]">
                        <EmotionsSentimentChart/>
                        <TopSubredditAppearancesChart/>
                        <EngagementMetricsChart />
                    </div>
                    <div className="bg-[#141414] mt-[5vh]">
                        <TopicSentimentsTimeChart/>
                    </div>
                    <div className="bg-[#141414] my-[5vh]">
                        <PostingFrequencyChart/>
                    </div>
                    <button 
                        className="fixed flex justify-center items-center bottom-8 right-12 w-12 h-12 bg-card hover:bg-logo rounded-xl border-2 border-interactive"
                    >
                        <MoonIcon/>
                    </button>
                </section>
            </div>
        </main>
    )
}