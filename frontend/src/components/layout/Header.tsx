import { useState } from "react";
import { Link } from "react-router";
import { Search } from "lucide-react";

interface HeaderProps {
  onSearch?: (query: string) => void;
}

const Header = ({ onSearch }: HeaderProps) => {
  const [query, setQuery] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    onSearch?.(e.target.value);
  };

  return (
    <header className="fixed top-0 left-0 right-0 h-14 bg-[#0a0a0a] border-b border-zinc-800/50 z-50">
      <div className="h-full px-6 flex items-center justify-between">
        <Link to="/" className="text-base font-semibold tracking-tight text-zinc-100 hover:text-white transition-colors">
          cyphria
        </Link>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={query}
            onChange={handleChange}
            placeholder="Search products..."
            className="w-64 pl-9 pr-4 py-1.5 text-sm bg-zinc-900/50 border border-zinc-800 rounded-lg text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
          />
        </div>
      </div>
    </header>
  );
}

export default Header