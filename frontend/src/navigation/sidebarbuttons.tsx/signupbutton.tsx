import { UserPlus } from "lucide-react"
import { useSelector } from "react-redux"
import { useNavigate } from "react-router"
import { selectExpandState } from "../../app/stateSlices/expandSlice"

export function SignUpButton() {
    const navigate = useNavigate()
    const expand = useSelector(selectExpandState)

    function handleNavigate() {
        navigate("/signup")
    }

    return (
        <button className={`${expand ? "flex items-center space-x-6" : "flex flex-col"}`} onClick={handleNavigate}>
            <UserPlus className='text-gray-400 w-[30px] h-[30px] ml-2' strokeWidth={2.5}/>
            {expand && (
                <h1 className="font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2">Sign Up</h1>
            )}
        </button>
    )
}