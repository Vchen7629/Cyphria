import { ChartSpline } from "lucide-react";
import { useNavigate } from "react-router";

export function SubredditStatisticsButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/subreddit")
    }

    return (
        <button onClick={handleNavigate}>
            <ChartSpline className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}