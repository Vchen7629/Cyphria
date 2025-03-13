import { HeaderComponent } from "../components/header/header";
import { SidebarComponent } from "../components/sidebar";

export default function UserStatisticsPage() {
    return (
        <main className="flex w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <section className="flex flex-col w-full items-center font-bold">
                <HeaderComponent/>
                <span className="text-5xl">User Statistics page Under Construction</span>
            </section>
        </main>
    )
}