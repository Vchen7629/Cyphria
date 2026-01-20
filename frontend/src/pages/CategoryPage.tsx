import { useMemo } from "react";
import { useParams, Navigate, Link } from "react-router";
import { ChevronRight } from "lucide-react";
import MainLayout from "../components/layout/MainLayout";
import TopicCard from "../components/category/TopicCard";
import { getCategoryBySlug } from "../mock/mockData";
import type { ProductV3, Topic } from "../mock/types";
import TopProductsCard from "../components/category/TopProductsCard";
import TopProductsGrid from "../components/category/topProductsGrid";

const CategoryPage = () => {
  const { category: categorySlug } = useParams<{ category: string }>();

  const category = useMemo(() => {
    if (!categorySlug) return undefined;
    return getCategoryBySlug(categorySlug);
  }, [categorySlug]);

  if (!category) {
    return <Navigate to="/" replace />;
  }

  return (
    <MainLayout currentParentSlug={category.slug}>
      <div className="max-w-4xl mx-auto px-6 py-8">
        <nav className="flex items-center gap-2 text-sm mb-6">
          <Link
            to="/"
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            Home
          </Link>
          <ChevronRight className="w-4 h-4 text-zinc-600" />
          <span className="text-zinc-300">{category.name}</span>
        </nav>
        <section className="mb-7">
          <h1 className="text-2xl font-semibold text-zinc-100">{category.name}</h1>
          <p className="text-sm text-zinc-500 mt-1">
            {category.topics.length} topics · 1000 products ranked
          </p>
        </section>
        <section className="mb-8">
          <h1 className="text-xl font-light text-zinc-200">Top mentioned products</h1>
          <TopProductsGrid categorySlug={categorySlug}/>
        </section>
        
        <section className="mb-8">
          <h1 className="text-xl font-light text-zinc-200">All product topics</h1>
          <div className="space-y-3 mt-4">
            {category.topics.map((topic: Topic) => (
              <TopicCard key={topic.id} topic={topic} />
            ))}
          </div>
        </section>
      </div>
    </MainLayout>
  );
}

export default CategoryPage