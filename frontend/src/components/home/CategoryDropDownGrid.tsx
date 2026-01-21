import {Monitor } from "lucide-react";
import iconMap from "../../utils/home/IconMap";
import type { Category } from "../../mock/types";
import { Link } from "react-router";
/**
 @component

 @description - Dropdown grid that displays all topics for a selected category

 @param {Category} category - the category object with all topics
 */
const CategoryDropDownGrid = ({ category }: { category: Category }) => {
  const IconComponent = iconMap[category.icon] || Monitor;

  return (
    <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-700/20">
      <section className="flex justify-between items-center mb-4">
        <span className="flex items-center text-sm text-zinc-400">
          <IconComponent className="w-5 h-5 mr-2 text-zinc-400" />
          {category.name} topics
        </span>
        <Link 
            to={`/${category.slug}`}
            className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
            View all
        </Link>
      </section>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {category.topics.map((topic) => (
          <div
            key={topic.id}
            className="p-3 rounded-md bg-zinc-800/40 hover:bg-zinc-800/60 border border-zinc-700/50 hover:border-zinc-600/50 transition-colors cursor-pointer"
          >
            <h4 className="text-sm font-medium text-zinc-300">{topic.name}</h4>
            <span className="text-xs text-zinc-500 mt-1">
                {topic.productCount} products | 500,000 opinions
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CategoryDropDownGrid