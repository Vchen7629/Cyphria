import type { ReactNode } from "react";

interface SidebarSectionProps {
  title: string;
  children: ReactNode;
}

/**
    @component

    @description - Layout for a sidebar section, title is the category and children
    are the individual topics buttons belonging to the category

    @param {string} title - the category topic
    @param {ReactNode} children - the individual topic buttons belonging to the category
 */
const SidebarSectionLayout = ({ title, children }: SidebarSectionProps) => {
  return (
    <div>
      <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider px-2 mb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

export default SidebarSectionLayout