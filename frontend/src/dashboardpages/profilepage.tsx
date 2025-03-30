import { Home } from "lucide-react";
import { HeaderComponent } from "../components/header/header";
import { SidebarComponent } from "../components/sidebar";

export default function ProfilePage() {
    return (
        <main className="flex w-[100vw] h-[100vh] bg-background">
            <SidebarComponent/>
            <section className="flex flex-col w-full items-center font-bold">
                <HeaderComponent/>
                <span className="text-5xl">Profile page Under Construction</span>
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