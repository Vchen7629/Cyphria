import { ArrowRightLeft, MoonIcon } from "lucide-react"
import { HeaderComponent } from "../components/header/header"
import { SidebarComponent } from "../components/sidebar"
import { DatePickerWithRange } from "../components/TopicTrendsPageComponents/datefilter"
import { TopicSentimentsTimeChart} from "../components/TopicTrendsPageComponents/TopicSentimentsChart"
import { selectExpandState } from "../app/stateSlices/expandSlice"
import { useSelector } from "react-redux"

const ComparisonPage = () => {
    const expand = useSelector(selectExpandState)

    return (
        <main className="flex  w-[100vw] h-[100vh] bg-background p-[1vw]">
            <SidebarComponent/>
            <div className={`flex flex-col ${expand ? "w-[87%] px-[4%]" : "w-[95vw] px-[3%]"} font-bold  overflow-auto`}>
                <HeaderComponent/>
                <section className="flex flex-col w-full overflow-auto">
                    <div className="relative flex items-center w-full h-[10vh] my-[3vh]  space-x-[2vw]">
                        <div className="flex justify-center items-center">   
                            <ArrowRightLeft className="w-10 h-10"/>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-lg">"Technology" vs "Fitness"</span>
                            <span className="text-sm text-gray-400">Sentiment enhanced Comparison</span>
                        </div>
                        <div className="absolute right-0">
                           <DatePickerWithRange/> 
                        </div>
                    </div>
                    <div className="bg-[#141414] w-[25vw] h-[40vh] pl-[1.5vw] pt-[1.5vh] mt-[2vh] rounded-2xl border-2 border-bordercolor">
                        <header className="w-full h-fit py-2">
                            <span className="text-2xl font-thin text-gray-400">Trending Topics</span>
                        </header>
                    </div>
                    <div className="bg-[#141414] mt-[5vh]">
                        <TopicSentimentsTimeChart/>
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

export default ComparisonPage