import { TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router';

export function TrendsButton() {
    const navigate = useNavigate();

    function handleNavigate() {
        navigate("/trendingtopics")
    }

    return (
        <button onClick={handleNavigate}>
            <TrendingUp className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}