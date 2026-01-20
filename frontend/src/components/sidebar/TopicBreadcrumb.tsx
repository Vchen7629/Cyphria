import { Link } from "react-router";
import { ChevronRight } from "lucide-react";

interface TopicBreadcrumbProps {
  parentName: string;
  parentSlug: string;
  topicName: string;
}

/**
 @Component

 @description - Navigation breadcrumb that displays on each topic page. 
 Allows the use to navigate back to the parent category or homepage
 
 @param {string} parentName - Parent Category name
 @param {string} parentSlug - Endpoint for parent category
 @param {string} topicName - Name of the current page topic
 */
const TopicBreadcrumb = ({
  parentName,
  parentSlug,
  topicName
}: TopicBreadcrumbProps) => {
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
      <span className="text-zinc-300">{topicName}</span>
    </nav>
  );
}

export default TopicBreadcrumb