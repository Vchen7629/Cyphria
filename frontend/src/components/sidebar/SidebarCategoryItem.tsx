import { useState } from "react";
import { Link } from "react-router";
import { ChevronRight, Monitor, Headphones, Smartphone, Gamepad2, Camera, Home } from "lucide-react";
import SidebarSubcategoryItem from "./SidebarTopicItem";
import type { Category } from "../../mock/types";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  Monitor,
  Headphones,
  Smartphone,
  Gamepad2,
  Camera,
  Home,
};

interface SidebarCategoryItemProps {
  category: Category;
  currentParent?: boolean;
  currentTopicSlug?: string;
  defaultExpanded?: boolean;
}

const SidebarCategoryItem = ({ category, currentParent, currentTopicSlug, defaultExpanded = false}: SidebarCategoryItemProps) => {
  const [isExpanded, setIsExpanded] = useState(
    defaultExpanded || category.topics.some(topic => topic.slug === currentTopicSlug) && currentParent
  );

  const IconComponent = iconMap[category.icon] || Monitor;
  const subcategoryCount = category.topics.length;

  return (
    <li>
      <div className="flex items-center">
        <Link
          to={`/${category.slug}`}
          className="flex-1 flex items-center gap-2 px-2 py-1.5 rounded-md text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 transition-colors"
        >
          <IconComponent className="w-4 h-4 text-zinc-500" />
          <span className="flex-1">{category.name}</span>
          <span className="text-xs text-zinc-600">({subcategoryCount})</span>
        </Link>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50 transition-colors"
          aria-label={isExpanded ? "Collapse" : "Expand"}
        >
          <ChevronRight
            className={`w-3.5 h-3.5 transition-transform ${isExpanded ? "rotate-90" : ""}`}
          />
        </button>
      </div>

      {isExpanded && (
        <ul className="ml-6 mt-1 space-y-0.5">
          {category.topics.map((topic) => (
            <SidebarSubcategoryItem
              key={topic.id}
              topic={topic}
              isActive={topic.slug === currentTopicSlug}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default SidebarCategoryItem