import { TextSearch } from 'lucide-react';
import { useNavigate } from 'react-router';

export function SearchButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/search")
    }

    return (
        <button onClick={handleNavigate}>
            <TextSearch className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}