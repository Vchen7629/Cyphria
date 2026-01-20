import SidebarCategoryItem from "./SidebarCategoryItem";
import type { Category } from "../../mock/types";

interface SidebarCategoryTreeProps {
  categories: Category[];
  currentParent?: boolean;
  currentTopicSlug?: string;
  defaultExpanded?: boolean;
}

/**
 @component

 @description - tree component that creates the list of categories
 containing a sublist of topic buttons belonging to the category

 @param {Category[]} categories - list of categories we are mapping
 @param {boolean} currentParent - Optional boolean flag used to check
 if we are on a topic page and disable the active state for the other
 2 list items
 @param {string} currentTopicSlug - Optional string for the current page
 topic endpoint
 @param {boolean} defaultExpanded - Optional boolean flag 
 */
const SidebarCategoryTree = ({
  categories,
  currentParent,
  currentTopicSlug,
  defaultExpanded = false
}: SidebarCategoryTreeProps) => {
  return (
    <ul className="space-y-1">
      {categories.map((category) => (
        <SidebarCategoryItem
          key={category.id}
          category={category}
          currentParent={currentParent}
          currentTopicSlug={currentTopicSlug}
          defaultExpanded={defaultExpanded}
        />
      ))}
    </ul>
  );
}

export default SidebarCategoryTree