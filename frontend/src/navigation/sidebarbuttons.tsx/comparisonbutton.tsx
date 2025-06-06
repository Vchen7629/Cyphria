import { GitCompareArrows } from "lucide-react";
import { useLocation, useNavigate } from "react-router";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { selectExpandState } from "../../app/stateSlices/expandSlice";

export function ComparisonButton() {
    const navigate = useNavigate();
    const location = useLocation();
    const expand = useSelector(selectExpandState)
    const [active, setActive] = useState(false)

    function handleNavigate() {
        navigate("/comparison")
    }

    useEffect(() => {
        if (location.pathname === "/comparison") {
            setActive(true)
        }
    }, [location])

    return (
        <button className={`${expand ? "flex items-center space-x-4" : "flex flex-col"}`} onClick={handleNavigate}>
            <GitCompareArrows className={`${active ? "text-test1" : "text-white"} w-[25px] h-[25px]`} strokeWidth={2.5}/>
            {expand && (
                <h1 className="font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2 ">Compare Topics</h1>
            )}
        </button>
    )
}