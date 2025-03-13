import { useNavigate } from "react-router"
import Logo from "../../assets/logo.svg"

export default function HomepageHeader() {
    const navigate = useNavigate();

    function handleHome() {
        navigate("/")
    }

    function handleFeatures() {
        navigate("/navigate")
    }   

    function handleContact() {
        navigate("/contact")
    }

    function handleGetStarted() {
        navigate("/search")
    }


    return (
        <main className="flex items-center justify-between h-[8vh] w-[70vw] bg-[#1D1D1E] px-[2rem] rounded-xl shadow-lg">
            <div className="flex space-x-4 items-center">
                <img src={Logo} alt="Logo" className="w-12 h-12" />
                <h1 className="text-lg font-roboto text-transparent bg-clip-text font-extrabold bg-gradient-to-r from-test1 to-test2">Cyphria</h1>
            </div>
            <div className="flex w-3/4 justify-center space-x-[10%]">
                <button onClick={handleHome}>
                    <span className="font-thin text-lg hover:text-test1">Home</span>
                </button>
                <button onClick={handleFeatures}>
                    <span className="font-thin text-lg hover:text-test1">Features</span>
                </button>
                <button onClick={handleContact}>
                    <span className="font-thin text-lg hover:text-test1">Contact</span>
                </button>
            </div>
            <button onClick={handleGetStarted} className="flex items-center justify-center h-[60%] w-[8%] bg-gray-600 rounded-lg">
                <span className="font-bold text-gray-200">Get Started</span>
            </button>
        </main>
    )
}