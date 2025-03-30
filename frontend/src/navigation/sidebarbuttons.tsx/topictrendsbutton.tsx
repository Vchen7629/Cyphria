import { MessageSquareShare } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router';
import { expand } from './types';
import { useEffect, useState } from 'react';

export function TopicButton({ expand }: expand) {
    const navigate = useNavigate()
    const location = useLocation();
    const [active, setActive] = useState(false)

    useEffect(() => {
        if (location.pathname === "/topic") {
            setActive(true)
        }
    }, [location])

    function handleNavigate() {
        navigate("/topic")
    }

    return (
        <button className={`${expand ? "flex items-center space-x-4" : "flex flex-col"}`} onClick={handleNavigate}>
            <MessageSquareShare className={`${active ? "text-test1": "text-white"} w-[25px] h-[25px]`} strokeWidth={2.5}/>
            {expand && (
                <h1 className="font-bold text-gray-300 font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2">Topic Trends</h1>
            )}
        </button>
    )
}