import { useMemo } from "react";
import { getTopProductsByCategory } from "../../utils/category/getTopProductsByCategory";
import { ProductV3 } from "../../mock/types";
import { Link } from "react-router";
import { getGradeColors } from "../../utils/product/GetColors";
import { ChevronRight } from "lucide-react";

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
                    {topProducts.slice(0,6).map((product: ProductV3) => {
                        const gradeColors = getGradeColors(product.grade);
    
                        return (
                            <Link
                                to={`/${product.parentSlug}/${product.subcategory_slug}`} 
                                className="flex flex-col animate-fade-in-up duration-500 justify-center space-y-2 p-4 rounded-lg text-zinc-400 hover:text-zinc-500 border border-zinc-600/50 bg-zinc-700/20 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
                            >
                                <section className="flex items-center space-x-2">
                                    <div className={`flex items-center justify-center w-8 h-6 rounded-lg border ${gradeColors.border} ${gradeColors.bg}`}>
                                        <span className="text-sm font-semibold">{product.grade}</span>
                                    </div>
                                    <span className="text-xs text-zinc-400 font-semibold">{product.mention_count} mentions</span>
                                </section>
                                <section>
                                    <span className="font-bold text-sm">{product.product_name}</span>
                                </section>
                                <section className="flex items-center space-x-1">
                                    <span  className="text-xs text-white">Topic:</span>
                                    <span className="text-xs">{product.subcategory_slug}</span>
                                    <ChevronRight size={13} className="mt-1"/>
                                </section>
                            </Link>
                        )
                    })}
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