import { FILTER_OPTIONS } from "../../mock/constants";
import type { FilterType } from "../../mock/types";

interface FilterTabsProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
}

/**
  @component

  @description - Component for the 4 tabs, Best Overall, Most Discussed, Highest Approval
  Hidden Gems on each product topic page
 */
const FilterTabs = ({ activeFilter, onFilterChange }: FilterTabsProps) => {
  return (
    <div className="flex gap-6 border-b border-zinc-800/50">
      {FILTER_OPTIONS.map((option) => (
        <button
          key={option.id}
          onClick={() => onFilterChange(option.id as FilterType)}
          className={`text-sm pb-3 border-b-2 transition-colors ${
            activeFilter === option.id
              ? "text-zinc-100 border-zinc-100"
              : "text-zinc-500 border-transparent hover:text-zinc-300"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

export default FilterTabs