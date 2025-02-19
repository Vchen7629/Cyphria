import { HeaderComponent } from "../components/header";
import { SidebarComponent } from "../components/sidebar";

export default function SearchPage() {

    return (
        <main className="flex  w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <div className="flex flex-col w-full items-center font-bold">
                <HeaderComponent/>
                <span className="text-5xl">
                SearchPage Under Construction
                </span>
            </div>
        </main>
    )
}