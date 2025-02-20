import { User } from 'lucide-react';
import { useNavigate } from 'react-router';

export function UserStatisticsButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/userstatistics")
    }
    
    return (
        <button onClick={handleNavigate}>
            <User className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}