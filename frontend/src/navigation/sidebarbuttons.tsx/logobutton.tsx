import { useNavigate } from "react-router"
import Logo from "../../assets/logo.svg"

export function LogoButton() {
    const navigate = useNavigate()
    
    function handleNavigate() {
        navigate("/")
    }

    return (
        <button onClick={handleNavigate}>
            <img src={Logo} alt="Logo" className="w-12 h-12 mb-[5vh]" />
        </button>
    )
}