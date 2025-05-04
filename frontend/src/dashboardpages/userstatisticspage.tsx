import { useSelector } from "react-redux";
import { HeaderComponent } from "../components/header/header";
import { SidebarComponent } from "../components/sidebar";
import { selectExpandState } from "../app/stateSlices/expandSlice";
import { MoonIcon } from "lucide-react";

export default function UserStatisticsPage() {
    const expand = useSelector(selectExpandState)
    return (
        <main className="flex w-[100vw] h-[100vh] bg-background p-[1vw]">
            <SidebarComponent/>
            <div className={`flex flex-col ${expand ? "w-[87%] px-[4%]" : "w-[95vw] px-[3%]"} font-bold  overflow-auto`}>
                <HeaderComponent/>
                <span className="text-5xl mt-[5vh]">User Statistics page Under Construction</span>
                <a 
                    className="fixed flex justify-center items-center bottom-4 right-4 w-12 h-12 bg-card hover:bg-logo rounded-xl border-2 border-interactive"
                    href="/"
                >
                    <MoonIcon/>
                </a>
            </div>
        </main>
    )
}