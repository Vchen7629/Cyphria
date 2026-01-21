import { Search } from "lucide-react"

interface ProductSearchBarProps {
    query: string
    setQuery: React.Dispatch<React.SetStateAction<string>>
}
/**
    @component

    @description - Searchbar component for filtering the products on the current product topic
    page

    @param {string} query - the search query string
    @param {React.Dispatch<React.SetStateAction<string>>} setQuery - the setter to set the query on
 */
const TopicProductSearchBar = ({ query, setQuery }: ProductSearchBarProps) => {

    function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
        setQuery(e.target.value);
    };

    return (
        <div className="relative bottom-2.5">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
                type="text"
                value={query}
                onChange={handleChange}
                placeholder="Search products from this topic..."
                className="w-64 pl-9 pr-4 py-1.5 text-sm bg-zinc-900/50 border border-zinc-800 rounded-lg text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
            />
        </div>
    )
}

export default TopicProductSearchBar