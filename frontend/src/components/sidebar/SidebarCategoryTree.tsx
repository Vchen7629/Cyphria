import SidebarCategoryItem from "./SidebarCategoryItem";
import type { Category } from "../../mock/types";

interface SidebarCategoryTreeProps {
  categories: Category[];
  currentTopicSlug?: string;
  defaultExpanded?: boolean;
}

const SidebarCategoryTree = ({
  categories,
  currentTopicSlug,
  defaultExpanded = false
}: SidebarCategoryTreeProps) => {
  return (
    <ul className="space-y-1">
      {categories.map((category) => (
        <SidebarCategoryItem
          key={category.id}
          category={category}
          currentTopicSlug={currentTopicSlug}
          defaultExpanded={defaultExpanded}
        />
      ))}
    </ul>
  );
}

export default SidebarCategoryTree