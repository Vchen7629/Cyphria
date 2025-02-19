import { User } from 'lucide-react';
import { useNavigate } from 'react-router';

export function UserButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/profile")
    }
    
    return (
        <button onClick={handleNavigate}>
            <User className='text-interactive w-[30px] h-[30px]' strokeWidth={2.5}/>
        </button>
    )
}