import Logo from "../../assets/logo.svg"
import { FlickeringGrid } from "../../ui/magicui/flickering-grid";

export function LoginLogo() {
    return (
        <div className="w-full h-fit flex items-center justify-center space-x-2">
            <FlickeringGrid
                className="flex w-fit h-10 mt-4 mr-[-0.5vw]"
                squareSize={2.5}
                gridGap={6}
                color="#6B7280"
                maxOpacity={0.5}
                width={100}
                flickerChance={0.01}
            />
            <div className="flex justify-center items-center w-18 h-18 bg-card shadow-lg rounded-xl">
                <img src={Logo} alt="Logo" className="w-16 h-16" />
            </div>
            <FlickeringGrid
                className="flex w-fit h-10 mt-4"
                squareSize={2.5}
                gridGap={6}
                color="#6B7280"
                maxOpacity={0.5}
                width={100}
                flickerChance={0.01}
            />
        </div>
    )
}