import { Link } from "react-router";
import { ChevronRight } from "lucide-react";

interface SubcategoryBreadcrumbProps {
  parentName: string;
  parentSlug: string;
  subcategoryName: string;
}

/**
 @Component

 @description - Navigation breadcrumb that displays on each subcategory page. 
 Allows the use to navigate back to the parent category or homepage
 
 @param {string} parentName - Parent Category name
 @param {string} parentSlug - Endpoint for parent category
 @param {string} subcategoryName - Name of the current page subcategory
 */
const SubcategoryBreadcrumb = ({
  parentName,
  parentSlug,
  subcategoryName
}: SubcategoryBreadcrumbProps) => {
  return (
    <nav className="flex items-center gap-2 text-sm">
      <Link
        to="/"
        className="text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        Home
      </Link>
      <ChevronRight className="w-4 h-4 text-zinc-600" />
      <Link
        to={`/${parentSlug}`}
        className="text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        {parentName}
      </Link>
      <ChevronRight className="w-4 h-4 text-zinc-600" />
      <span className="text-zinc-300">{subcategoryName}</span>
    </nav>
  );
}

export default SubcategoryBreadcrumb