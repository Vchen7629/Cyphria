import { LogIn } from 'lucide-react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import { selectExpandState } from '../../app/stateSlices/expandSlice';

export function LoginButton() {
    const navigate = useNavigate()
    const expand = useSelector(selectExpandState)

    function handleLogin() {
        navigate("/login")
    }

    return (
        <button className={`${expand ? "flex items-center space-x-8" : "flex flex-col"}`} onClick={handleLogin}>
            <LogIn className='text-gray-400 w-[30px] h-[30px]'/>
            {expand && (
                <h1 className="font-bold text-gray-300 font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2">Login</h1>
            )}
        </button>
    )
}