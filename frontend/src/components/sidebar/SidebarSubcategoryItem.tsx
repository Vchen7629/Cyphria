import { Link } from "react-router";
import type { Topic } from "../../mock/types";

interface SidebarSubcategoryItemProps {
  topic: Topic;
  isActive?: boolean;
}

const SidebarSubcategoryItem = ({ topic, isActive = false }: SidebarSubcategoryItemProps) => {
  return (
    <li>
      <Link
        to={`/${topic.parentSlug}/${topic.slug}`}
        className={`block px-2 py-1 rounded-md text-sm transition-colors ${
          isActive
            ? "text-zinc-100 bg-zinc-800/70"
            : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/30"
        }`}
      >
        {topic.name}
      </Link>
    </li>
  );
}

export default SidebarSubcategoryItem