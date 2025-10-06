import { ArrowLeftFromLine } from "lucide-react"
import { useDispatch } from "react-redux"
import { toggleExpand } from "../../../app/state/ui"

export function ExpandButton() {    
    const dispatch = useDispatch()

    function ToggleExpand() {
        dispatch(toggleExpand())
    }

    return (
        <button className="flex items-center space-x-2" onClick={ToggleExpand}>
            <ArrowLeftFromLine className="text-gray-400 w-[20px] h-[20px]" strokeWidth={2.5}/>
        </button>
    )
}