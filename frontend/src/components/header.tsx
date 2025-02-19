import { TextSearch, User } from "lucide-react";
import { useLocation } from "react-router";

export function HeaderComponent() {
    const location = useLocation();

    return (
        <header className="flex border-b-[1px] justify-between items-center border-bordercolor h-[10vh] w-[100%] mb-[10vh] px-[3vw]">
            <div className="flex items-center space-x-[2vw]">
                <div className="flex w-12 h-12 rounded-xl justify-center bg-logo items-center">
                    <TextSearch />
                </div>
                <span className="text-xl font-bold">{location.pathname.slice(1, 30)}</span>
            </div>
            <div className="flex space-x-3 items-center border-2 border-bordercolor bg-card py-1 px-2 rounded-xl">
                <div className="bg-gray-700 p-2 rounded-xl border-2 border-test2">
                    <User className="h-6 w-6"/>
                </div>
                <span className="text-md">Placeholder Username</span>
            </div>
        </header>
    )
}