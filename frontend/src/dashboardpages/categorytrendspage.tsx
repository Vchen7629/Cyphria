import { Home, Layers } from "lucide-react";
import { HeaderComponent } from "../components/header/header";
import { SidebarComponent } from "../components/sidebar";
import { DatePickerWithRange } from "../components/TopicTrendsPageComponents/datefilter";
import { TopicSentimentsTimeChart} from "../components/TopicTrendsPageComponents/TopicSentimentsChart";
import { selectExpandState } from "../app/stateSlices/expandSlice";
import { useSelector } from "react-redux";

export default function SentimentEnhancedTrendsPage() { 
    const expand = useSelector(selectExpandState)
    
    return (
        <main className="flex  w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <div className={`flex flex-col ${expand ? "w-[85vw]" : "w-[95vw]"} font-bold`}>
                <HeaderComponent/>
                <section className="flex flex-col ml-[5vw] overflow-auto">
                    <div className="relative flex items-center w-full h-[10vh] mt-[3vh]  space-x-[2vw]">
                        <div className="flex justify-center items-center">   
                            <Layers className="w-10 h-10"/>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-lg">Trends for "Technology"</span>
                            <span className="text-sm text-gray-400">Sentiment enhanced trends</span>
                        </div>
                        <div className="absolute right-[3vw]">
                           <DatePickerWithRange/> 
                        </div>
                    </div>
                    <div className="bg-[#141414] w-[25vw] h-[40vh] pl-[1.5vw] pt-[1.5vh] mt-[2vh] rounded-2xl border-2 border-bordercolor">
                        <header className="w-full h-fit py-2">
                            <span className="text-2xl font-thin text-gray-400">Trending Topics</span>
                        </header>
                    </div>
                    <div className="bg-[#141414] w-[95%] mt-[5vh]">
                        <TopicSentimentsTimeChart/>
                    </div>
                    <a 
                        className="fixed flex justify-center items-center bottom-4 right-4 w-12 h-12 bg-card hover:bg-logo rounded-xl border-2 border-interactive"
                        href="/"
                    >
                        <Home/>
                    </a>
                    
                </section>
            </div>
        </main>
    )
}