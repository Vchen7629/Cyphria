import { Bookmark } from "lucide-react";
import { useNavigate } from "react-router";

export function BookmarkButton() {
    const navigate = useNavigate()

    function handleNavigate() {
        navigate("/bookmarks")
    }

    return (
        <button onClick={handleNavigate}>
            <Bookmark className='text-white  w-[25px] h-[25px]' strokeWidth={2.5}/>
        </button>
    )
}