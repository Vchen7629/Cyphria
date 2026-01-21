import React from "react"

interface PriceFilterSwitchProps {
    selectedPrice: '$' | '$$' | '$$$' | null
    setSelectedPrice: React.Dispatch<React.SetStateAction<'$' | '$$' | '$$$' | null>>
}

const PriceFilterSwitch = ({ selectedPrice, setSelectedPrice }: PriceFilterSwitchProps) => {
    function handlePriceClick(price: '$' | '$$' | '$$$') {
        setSelectedPrice(prev => prev === price ? null : price)
    }

    return (
        <div className="flex gap-1 relative bottom-2.5">
            <button
                onClick={() => handlePriceClick("$")}
                className={`px-2 py-1 text-xs rounded-md border transition-colors ${
                    selectedPrice === "$"
                        ? "bg-zinc-100 text-zinc-900 border-zinc-100"
                        : "bg-zinc-900/50 text-zinc-400 border-zinc-800 hover:text-zinc-300 hover:border-zinc-600"
                }`}
            >
                $
            </button>
            <button
                onClick={() => handlePriceClick("$$")}
                className={`px-2 py-1 text-xs rounded-md border transition-colors ${
                    selectedPrice === "$$"
                        ? "bg-zinc-100 text-zinc-900 border-zinc-100"
                        : "bg-zinc-900/50 text-zinc-400 border-zinc-800 hover:text-zinc-300 hover:border-zinc-600"
                }`}
            >
                $$
            </button>
            <button
                onClick={() => handlePriceClick("$$$")}
                className={`px-2 py-1 text-xs rounded-md border transition-colors ${
                    selectedPrice === "$$$"
                        ? "bg-zinc-100 text-zinc-900 border-zinc-100"
                        : "bg-zinc-900/50 text-zinc-400 border-zinc-800 hover:text-zinc-300 hover:border-zinc-600"
                }`}
            >
                $$$
            </button>
        </div>
    )
}

export default PriceFilterSwitch