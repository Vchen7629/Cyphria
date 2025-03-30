import { LogIn } from 'lucide-react';
import { useNavigate } from 'react-router';
import { expand } from './types';

export function LoginButton({ expand }: expand) {
    const navigate = useNavigate()

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