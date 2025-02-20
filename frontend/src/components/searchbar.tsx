import { useState } from "react";
import { Search, X } from "lucide-react";

export function SearchBar() {
    const [searchTerm, setSearchTerm] = useState("")

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        const inputValue = e.target.value;
        setSearchTerm(inputValue);;
    };

    function handleClearClick() {
        setSearchTerm("")
    }

    return (
        <div className="flex items-center w-[50vw] h-[5vh] bg-[#141414] border-[1px] border-bordercolor rounded-xl px-4 space-x-4">
            <Search/>
            <input
                className="flex bg-transparent w-full h-full text-lg focus:outline-none"
                type="text"
                value={searchTerm}
                onChange={handleInputChange}
                placeholder="Search"
            />
            {searchTerm && (
                <button className="cursor-pointer bg-transparent" onClick={handleClearClick}>
                    <X/>
                </button>
            )}
        </div>
    )
}