import { ChartNoAxesCombined } from "lucide-react";
import { useNavigate } from "react-router";

export function TemporalAnalysisButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/temporal")
    }

    return (
        <button onClick={handleNavigate}>
            <ChartNoAxesCombined className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}