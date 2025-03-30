import { GitCompareArrows } from "lucide-react";
import { useNavigate } from "react-router";

export function ComparisonButton() {
    const navigate = useNavigate();

    function handleNavigate() {
        navigate("/comparison")
    }

    return (
        <button onClick={handleNavigate}>
            <GitCompareArrows className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}