import { MessageSquareShare } from 'lucide-react';
import { useNavigate } from 'react-router';

export function TopicButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/topic")
    }

    return (
        <button onClick={handleNavigate}>
            <MessageSquareShare className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}