import { Bookmark } from "lucide-react";
import { useLocation, useNavigate } from "react-router";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { selectExpandState } from "../../app/stateSlices/expandSlice";

export function BookmarkButton() {
    const navigate = useNavigate()
    const location = useLocation();
    const [active, setActive] = useState(false)
    const expand = useSelector(selectExpandState)

    useEffect(() => {
        if (location.pathname === "/bookmarks") {
            setActive(true)
        }
    }, [location])

    function handleNavigate() {
        navigate("/bookmarks")
    }

    return (
        <button className={`${expand ? "flex items-center space-x-4" : "flex flex-col"}`} onClick={handleNavigate}>
            <Bookmark className={`${active ? "text-test2" : "text-white"} w-[25px] h-[25px]`} strokeWidth={2.5}/>
            {expand && (
                <h1 className="font-bold text-gray-300 font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2">Bookmarks</h1>
            )}
        </button>
    )
}