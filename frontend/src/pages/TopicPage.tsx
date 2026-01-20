import { useState, useMemo } from "react";
import { useParams, Navigate } from "react-router";
import MainLayout from "../components/layout/MainLayout";
import TopicBreadCrumb from "../components/sidebar/TopicBreadcrumb";
import ProductList from "../components/product/ProductList";
import { mockComments } from "../mock/mockData";
import type { FilterType } from "../mock/types";
import FilterTabs from "../components/product/FilterTabs";
import { getTopicBySlug } from "../utils/topic/GetTopicBySlug";
import { getProducts } from "../utils/topic/GetProducts";

const TopicPage = () => {
  const { category: categorySlug, topic: topicSlug } = useParams<{
    category: string;
    topic: string;
  }>();

  const [activeFilter, setActiveFilter] = useState<FilterType>("best");
  const [isLoading, setIsLoading] = useState(false);

  const categoryData = useMemo(() => {
    if (!categorySlug || !topicSlug) return undefined;
    return getTopicBySlug(categorySlug, topicSlug);
  }, [categorySlug, topicSlug]);

  const products = useMemo(() => getProducts(topicSlug), [topicSlug]);

  const filteredProducts = useMemo(() => {
    const sorted = [...products];

    switch (activeFilter) {
      case "best":
        return sorted.sort((a, b) => a.rank - b.rank);
      case "discussed":
        return sorted.sort((a, b) => b.mention_count - a.mention_count);
      case "approval":
        return sorted.sort((a, b) => b.approval_percentage - a.approval_percentage);
      case "hidden_gems":
        return sorted.filter((p) => p.is_hidden_gem || (p.approval_percentage > 75 && p.mention_count < 500));
      default:
        return sorted;
    }
  }, [products, activeFilter]);

  const handleFilterChange = (filter: FilterType) => {
    setIsLoading(true);
    setActiveFilter(filter);
    setTimeout(() => setIsLoading(false), 200);
  };

  if (!categoryData) {
    return <Navigate to="/" replace />;
  }

  const { parent, topic: sub } = categoryData;

  return (
    <MainLayout
      currentParentSlug={parent.slug}
      currentTopicSlug={sub.slug}
    >
      <main className="max-w-4xl mx-auto px-6 py-8">
        <TopicBreadCrumb
          parentName={parent.name}
          parentSlug={parent.slug}
          topicName={sub.name}
        />

        <section className="mt-6 mb-8">
          <h1 className="text-2xl font-semibold text-zinc-100">Best {sub.name} based on reddit opinions </h1>
          <p className="text-sm text-zinc-500 mt-1">
            {filteredProducts.length} products ranked from Reddit discussions
          </p>
        </section>

        <div className="mb-6">
          <FilterTabs activeFilter={activeFilter} onFilterChange={handleFilterChange} />
        </div>

        <div className="border border-zinc-600/50 rounded-lg overflow-hidden">
          <ProductList
            products={filteredProducts}
            comments={mockComments}
            isLoading={isLoading}
          />
        </div>
      </main>
    </MainLayout>
  );
}

export default TopicPage