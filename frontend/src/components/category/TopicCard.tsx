import { Link } from "react-router";
import { CalendarCheck, ChevronRight, Dot } from "lucide-react";
import type { ProductV3, Topic } from "../../mock/types";
import { useMemo } from "react";
import { getProducts } from "../../utils/topic/GetProducts";
import TopMentionedProductCard from "./topMentionedProductCard";

interface TopicCardProps {
  topic: Topic;
}

const TopicCard = ({ topic }: TopicCardProps) => {
  const products = useMemo(() => getProducts(topic.slug), [topic.slug])

  return (
    <Link
      to={`/${topic.parentSlug}/${topic.slug}`}
      className="group flex items-center justify-between p-4 rounded-lg border border-zinc-600/50 bg-zinc-800/30 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
    >
      <div className="flex flex-col space-y-2">
        <h3 className="text-sm font-medium text-zinc-200 group-hover:text-zinc-100 transition-colors">
          {topic.name}
        </h3>
        <section className="flex items-center mt-1">
          <div className="flex items-center space-x-2">
            <CalendarCheck size={14} className="text-zinc-500"/>
            <span className="text-xs text-zinc-500">Last Updated Dec 2025</span>
          </div>
          <Dot size={20} className="text-zinc-400"/>
          <span className="text-xs text-zinc-500">{topic.productCount} products ranked</span>
        </section>
        <section className="flex flex-col">
          <span className="text-xs font-medium text-zinc-400">Most Discussed Products</span>
          <ul className="flex gap-2 mt-2">
            {products.length > 0 ? (
              products.slice(0,3).map((product: ProductV3) => (
                <TopMentionedProductCard key={product.id} product={product} />
              ))
            ) : (
              <div className="flex items-center space-x-1 py-1.5 px-2.5 bg-zinc-900 border border-zinc-700 rounded-lg w-fit">
                <span className="text-xs text-zinc-400">No products found</span>
              </div>
            )}
          </ul>
        </section>
      </div>
      <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
    </Link>
  );
}

export default TopicCard