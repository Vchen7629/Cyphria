import { useSelector } from "react-redux";
import { HeaderComponent } from "../components/header/header";
import { SidebarComponent } from "../components/sidebar";
import { selectExpandState } from "../app/stateSlices/expandSlice";
import { Home } from "lucide-react";

export default function BookmarkPage() {
    const expand = useSelector(selectExpandState)

    return (
        <main className="flex w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <section className={`flex flex-col ${expand ? "w-[85vw]" : "w-[95vw]"} font-bold items-center`}>
                <HeaderComponent/>
                <span className="text-5xl mt-[5vh]">Bookmark page Under Construction</span>
                <a 
                    className="fixed flex justify-center items-center bottom-4 right-4 w-12 h-12 bg-card hover:bg-logo rounded-xl border-2 border-interactive"
                    href="/"
                >
                    <Home/>
                </a>
            </section>
        </main>
    )
}