import { Link } from "react-router";
import type { Topic } from "../../mock/types";

interface SidebarTopicItemProps {
  topic: Topic;
  isActive?: boolean;
}

/**
  @component

  @description - Single navigation button item for a single topic in the sidebar topic list

  @param {Topic} topic - The topic this item is for
  @param {boolean} isActive - boolean flag that is set to true if the current page is the topic
 */
const SidebarTopicItem = ({ topic, isActive = false }: SidebarTopicItemProps) => {
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

export default SidebarTopicItem