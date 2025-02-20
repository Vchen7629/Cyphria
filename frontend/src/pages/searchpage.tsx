import { HeaderComponent } from "../components/header";
import { SearchBar } from "../components/searchbar";
import { SidebarComponent } from "../components/sidebar";

export default function SearchPage() {

    return (
        <main className="flex  w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <div className="flex flex-col w-full space-y-[5vh] font-bold">
                <HeaderComponent/>
                <section className="flex flex-col m-[5vw] space-y-[5vh]">
                    <SearchBar />
                    <span className="text-5xl "> SearchPage Under Construction</span>
                    <div className="bg-[#141414] w-[25vw] h-[40vh] rounded-2xl border-2 border-bordercolor">

                    </div>
                </section>
            </div>
        </main>
    )
}