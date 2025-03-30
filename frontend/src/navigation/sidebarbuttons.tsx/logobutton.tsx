import { useNavigate } from "react-router"
import Logo from "../../assets/logo.svg"
import { useSelector } from "react-redux"
import { selectExpandState } from "../../app/stateSlices/expandSlice"

export function LogoButton() {
    const navigate = useNavigate()
    const expand = useSelector(selectExpandState)
    
    function handleNavigate() {
        navigate("/")
    }

    return (
        <button className={`${expand ? "flex items-center space-x-2" : "flex flex-col"}`} onClick={handleNavigate}>
            <img src={Logo} alt="Logo" className={`${expand && "ml-[-0.5vw]"} w-12 h-12`}/>
            {expand && (
                <h1 className="text-lg font-roboto text-transparent bg-clip-text font-extrabold bg-gradient-to-r from-test1 to-test2">Cyphria</h1>
            )}
        </button>
    )
}