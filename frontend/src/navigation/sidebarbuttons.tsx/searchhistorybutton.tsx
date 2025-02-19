import { History } from "lucide-react"
import { useNavigate } from "react-router"

export function SearchHistoryButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/temporal")
    }

    return (
        <button onClick={handleNavigate}>
            <History className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}