import { ChartColumnStacked } from 'lucide-react';
import { useNavigate } from 'react-router';

export function CategoryTrendsButton() {
    const navigate = useNavigate();

    function handleNavigate() {
        navigate("/category")
    }

    return (
        <button onClick={handleNavigate}>
            <ChartColumnStacked className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}