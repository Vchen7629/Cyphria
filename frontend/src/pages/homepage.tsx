import { SidebarComponent } from '../../src/components/sidebar/sidebar';

export default function Homepage() {

    return (
        <main className="flex w-[100vw] h-[100vh] bg-background">
            <SidebarComponent />
            <p className="flex w-full justify-center items-center text-5xl font-bold">Homepage Under Construction</p>
        </main>
    )
}