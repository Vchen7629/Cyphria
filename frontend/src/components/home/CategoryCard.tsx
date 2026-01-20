import { Monitor, ChevronRight } from "lucide-react";
import { Link } from "react-router";
import iconMap from "../../utils/home/IconMap";
import type { Category } from "../../mock/types";

interface CategoryCardProps {
  category: Category;
}

const CategoryCard = ({ category }: CategoryCardProps) => {
  const IconComponent = iconMap[category.icon] || Monitor;

  return (
    <Link
      to={`/${category.slug}`}
      className="group block p-4 rounded-lg border border-zinc-600/50 bg-zinc-700/20 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-md bg-zinc-800/60">
            <IconComponent className="w-5 h-5 text-zinc-400" />
          </div>
          <h3 className="text-sm font-medium text-zinc-200 group-hover:text-zinc-100 transition-colors">
            {category.name}
          </h3>
        </div>
        <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
      </div>
      <p className="text-xs text-zinc-500 pl-11">
        {category.guideCount} guides · {category.topics.length} subcategories
      </p>
    </Link>
  );
}

export default CategoryCard