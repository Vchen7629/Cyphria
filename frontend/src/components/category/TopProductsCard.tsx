import { Link } from "react-router";
import type { ProductV3 } from "../../mock/types";
import { ChevronRight } from "lucide-react";
import { getGradeColors } from "../../utils/product/GetGradeColors";

interface topProductProp {
    product: ProductV3;
}

const TopProductsCard = ({ product }: topProductProp) => {
    const gradeColors = getGradeColors(product.grade);
    
    return (
        <Link 
            to={`/${product.parentSlug}/${product.subcategory_slug}`} 
            className="flex flex-col justify-center space-y-2 p-4 rounded-lg text-zinc-400 hover:text-zinc-500 border border-zinc-600/50 bg-zinc-700/20 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
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
}

export default TopProductsCard