import SidebarSection from "../layout/SideBarSectionLayout";
import SidebarCategoryTree from "./SidebarCategoryTree";
import type { Category } from "../../mock/types";
import { getPopularCategories } from "../../mock/mockData";

interface SidebarProps {
  categories: Category[];
  currentParentSlug?: string;
  currentTopicSlug?: string;
}

const Sidebar = ({ categories, currentParentSlug, currentTopicSlug }: SidebarProps) => {
  const popularCategories = getPopularCategories(categories);
  const currentParent = categories.find(cat => cat.slug === currentParentSlug);

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-[#0a0a0a] border-r border-zinc-600/50 pt-14 overflow-y-auto z-40">
      <nav className="py-4 px-3 space-y-6">
        {currentParent && (
          <SidebarSection title={`${currentParent.name} Categories`}>
            <SidebarCategoryTree
              categories={[currentParent]}
              currentTopicSlug={currentTopicSlug}
              defaultExpanded={true}
            />
          </SidebarSection>
        )}

        <SidebarSection title="Popular Categories">
          <SidebarCategoryTree
            categories={popularCategories}
            currentTopicSlug={currentTopicSlug}
          />
        </SidebarSection>

        <SidebarSection title="Browse">
          <SidebarCategoryTree
            categories={categories}
            currentTopicSlug={currentTopicSlug}
          />
        </SidebarSection>
      </nav>
    </aside>
  );
}

export default Sidebar