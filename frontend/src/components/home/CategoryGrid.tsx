import CategoryCard from "./CategoryCard";
import type { Category } from "../../mock/types";

export interface CategoryComponentProps {
  categories: Category[];
}

const CategoryGrid = ({ categories }: CategoryComponentProps) => {
  return (
    <section>
      <h2 className="text-lg font-medium text-zinc-100">Browse Categories</h2>
      <span className="text-sm font-light text-zinc-400"></span>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
        {categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </section>
  );
}

export default CategoryGrid
