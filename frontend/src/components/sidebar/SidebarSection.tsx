import type { ReactNode } from "react";

interface SidebarSectionProps {
  title: string;
  children: ReactNode;
}

const SidebarSection = ({ title, children }: SidebarSectionProps) => {
  return (
    <div>
      <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider px-2 mb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

export default SidebarSection