import { useMemo } from "react";
import { getTopProductsByCategory } from "../../utils/category/getTopProductsByCategory";
import { ProductV3 } from "../../mock/types";
import TopProductsCard from "./TopProductsCard";

interface TopProductsGridProps {
    categorySlug?: string 
}

const TopProductsGrid = ({ categorySlug }: TopProductsGridProps) => {
    const topProductLimit = 6

    const topProducts = useMemo(() => {
        if (!categorySlug) return [];
        return getTopProductsByCategory(categorySlug, topProductLimit);
    }, [categorySlug]);

    return (
        <div className="mt-4">
            {topProducts.length > 0 ? (
                <div className="grid grid-cols-3 gap-2 mt-4">
                    {topProducts.slice(0,6).map((product: ProductV3) => (
                        <TopProductsCard product={product}/>
                    ))}
                </div>
            ) : (
                <div className="border border-zinc-600/50 rounded-lg overflow-hidden">
                     <div className="py-12 text-center">
                        <p className="text-zinc-500 text-sm">No products found</p>
                    </div>
                </div>
            )}
        </div>
    )
}

export default TopProductsGrid