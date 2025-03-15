import { LogIn } from 'lucide-react';
import { useNavigate } from 'react-router';

export function LoginButton() {
    const navigate = useNavigate()

    function handleLogin() {
        navigate("/login")
    }

    return (
        <button onClick={handleLogin}>
            <LogIn className='text-gray-400 w-[30px] h-[30px]'/>
        </button>
    )
}