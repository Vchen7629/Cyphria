import type { ReactNode } from "react";
import Header from "./Header";
import Sidebar from "../sidebar/Sidebar";
import { mockCategories } from "../../mock/mockData";

interface MainLayoutProps {
  children: ReactNode;
  currentParentSlug?: string;
  currentTopicSlug?: string;
  showSidebar?: boolean;
}

const MainLayout = ({
  children,
  currentParentSlug,
  currentTopicSlug,
  showSidebar = true
}: MainLayoutProps) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-100">
      <Header />
      {showSidebar && (
        <Sidebar
          categories={mockCategories}
          currentParentSlug={currentParentSlug}
          currentTopicSlug={currentTopicSlug}
        />
      )}
      <main className={`${showSidebar ? "ml-60" : ""} pt-14`}>
        {children}
      </main>
    </div>
  );
}

export default MainLayout
