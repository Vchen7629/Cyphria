import { useLocation, useNavigate } from "react-router";
import { cloneElement, ReactNode, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { selectExpandState } from "../../../app/state/ui";

interface NavButtonProps {
    targetPage: string;
    label: string
    buttonIcon: ReactNode;
}

const NavButton = ({ targetPage, label, buttonIcon }: NavButtonProps) => {
    const navigate = useNavigate()
    const location = useLocation();
    const [active, setActive] = useState(false)
    const expand = useSelector(selectExpandState)

    useEffect(() => {
        if (location.pathname === targetPage) {
            setActive(true)
        }
    }, [location])

    function handleNavigate() {
        navigate(targetPage)
    }

    return (
        <button className={`${expand ? "flex items-center space-x-4" : "flex flex-col"}`} onClick={handleNavigate}>
            {cloneElement(buttonIcon as React.ReactElement, {
                className: `${active ? "text-test2" : "text-white"} w-[25px] h-[25px]`,
                strokeWidth: 2.5,
            } as any)}
            {expand && (
                <h1 className="font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2">
                    {label}
                </h1>
            )}
        </button>
    )
}

export default NavButton