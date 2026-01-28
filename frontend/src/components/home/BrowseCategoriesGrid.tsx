import { Fragment, useEffect, useMemo, useState } from "react"
import { Category } from "../../mock/types"
import { mockCategories } from "../../mock/mockData";
import iconMap from "../../utils/home/IconMap";
import { ChevronDown, Monitor } from "lucide-react";
import CategoryDropDownGrid from "./CategoryDropDownGrid";

/**
 @component

 @description - Parent Dropdown grid that displays all categories on home page
 */
const BrowseCateroriesGrid = () => {
    const [openCategoryId, setOpenCategoryId] = useState<string | null>(null);
    const [columnsPerRow, setColumnsPerRow] = useState<number>(3)
    const categories = mockCategories.slice(0, 6);

    // Detect screen size and update columns per row so its responsive
    useEffect(() => {
        function updateColumns() {
            if (window.innerWidth < 640) setColumnsPerRow(1); // sm window width breakpoint
            else if (window.innerWidth < 1024) setColumnsPerRow(2); // lg window width breakpoint
            else setColumnsPerRow(3)
        }

        updateColumns()
        window.addEventListener('resize', updateColumns)
        return () => window.removeEventListener('resize', updateColumns)
    }, [])

    // Group categories into rows based on columnsPerRow
    const browseCategoryRows = useMemo(() => {
        const rows: typeof categories[] = [];
        for (let i = 0; i < categories.length; i += columnsPerRow) {
            rows.push(categories.slice(i, i + columnsPerRow));
        }
        return rows;
    }, [categories, columnsPerRow])

    function toggleCategory(categoryId: string) {
        setOpenCategoryId(prev => prev === categoryId ? null : categoryId);
    };

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
            {browseCategoryRows.map((row: Category[], rowIndex) => (
            <Fragment key={`row-${rowIndex}`}>
                {row.map((category) => {
                    const IconComponent = iconMap[category.icon] || Monitor;

                    return (
                        <button
                            onClick={() => toggleCategory(category.id)}
                            className="p-4 rounded-lg border border-zinc-600/50 bg-zinc-700/20 hover:bg-zinc-800/30 hover:border-zinc-700/50 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-md bg-zinc-800/60"><IconComponent className="w-5 h-5 text-zinc-400" /></div>
                                <h3 className="text-sm font-medium text-zinc-200 group-hover:text-zinc-100 transition-colors">{category.name}</h3>
                            </div>
                            <section className="flex justify-between w-full mt-4">
                                <p className="text-xs text-zinc-500">{category.topics.length} Product topics</p>
                                <ChevronDown className={`w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-all ${openCategoryId === category.id ? 'rotate-180' : ''}`}/>
                            </section>
                        </button>
                    );
                })}
                {row.some((category) => category.id === openCategoryId) && (
                    <div className="col-span-full">
                        <CategoryDropDownGrid 
                            category={categories.find((c) => c.id === openCategoryId)!} 
                            toggleCategory={toggleCategory}
                        />
                    </div>
                )}
            </Fragment>
            ))}
        </div>
    )
}

export default BrowseCateroriesGrid