import type { ProductV3 } from "../../mock/types";

interface topProductProp {
    product: ProductV3;
}

const TopProductsCard = ({ product }: topProductProp) => {
    return (
        <div className="w-[20%] items-center p-4 rounded-lg text-zinc-300 hover:text-zinc-400 border border-zinc-600/50 bg-zinc-700/20 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors">
            <section className="flex items-center space-x-2">
                <div className="flex items-center justify-center w-6 h-6 rounded-lg bg-gray-800">
                    <span className="text-sm font-semibold">{product.grade}</span>
                </div>
            </section>
            <section>

            </section>
        </div>
    )
}

export default TopProductsCard