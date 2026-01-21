import { useEffect, useMemo, useState } from "react"
import { mockProducts } from "../../mock/mockData"
import { getGradeColors } from "../../utils/product/GetColors"
import { ProductV3 } from "../../mock/types"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Link } from "react-router"
import { FilterBySearchTerm } from "../../utils/product/productFilters"

/**
 @component

 @description - List that displays when the user types a search query on the searchbar on the header
 blurs the page background and displays a list of products matching the query

 @param {string} searchQuery - the user typed search query
 */
const AllProductsSearchList = ({ searchQuery }: { searchQuery: string }) => {
    const [currentPage, setCurrentPage] = useState<number>(1)
    const ITEMS_PER_PAGE = 6
    const allProducts = Object.values(mockProducts).flat()

    const filteredProducts = useMemo(() => {
        const productsList = [...allProducts]
        return FilterBySearchTerm(searchQuery, productsList)
    }, [allProducts, searchQuery]);

    const paginationInfo = useMemo(() => {
        const totalPages = Math.ceil(filteredProducts.length / ITEMS_PER_PAGE)
        const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
        const endIndex = startIndex + ITEMS_PER_PAGE

        return { totalPages, startIndex, endIndex }
    }, [filteredProducts.length, currentPage])

      // reset back to page 1 whenever search query changes
    useEffect(() => {
        setCurrentPage(1)
    }, [searchQuery])
    

    return (
        <ul className="absolute flex flex-col space-y-2 items-center right-6 w-80 h-fit bg-zinc-700/20 border border-zinc-500/20 rounded-lg p-4">
            <>
              {filteredProducts.length > 0 ? (
                filteredProducts.slice(paginationInfo.startIndex, paginationInfo.endIndex).map((product: ProductV3) => {
                  const gradeColors = getGradeColors(product.grade);

                  return (
                    <Link
                      key={product.id}
                      to={`/${product.parentSlug}/${product.subcategory_slug}`}
                      className="flex flex-col space-y-2 w-full bg-zinc-600/20 px-3 py-1.5 rounded-lg"
                    > 
                      <section className="flex group relative items-center space-x-2">
                        <div className={`flex items-center justify-center w-7 h-5 rounded-lg border ${gradeColors.border} ${gradeColors.bg} ${gradeColors.text}`}>
                          <span className="text-xs font-semibold">{product.grade}</span>
                        </div>
                        <span className="text-[13px] group-hover:text-zinc-400 transition-colors duration-250">{product.product_name}</span>
                        <ChevronRight className="absolute right-0 w-4 h-4 group-hover:text-zinc-500"/>
                      </section>
                      <section className="flex items-center">
                        <span className="text-xs mr-1 text-zinc-300">Topic: </span>
                        <span className="text-xs text-zinc-400 mr-4">{product.subcategory_slug}</span>
                        <span className="text-xs mr-1 text-zinc-300">Mentions:</span>
                        <span className="text-xs text-zinc-400 mr-4">{product.mention_count}</span>
                      </section>
                    </Link>
                  )
                })
              ) : (
                <span className="text-sm text-zinc-400">No products found for "{searchQuery}"</span>
              )}
              {paginationInfo.totalPages > 1 && (
                <div className="flex items-center">
                    <button
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        className="text-zinc-300 hover:text-zinc-300 disabled:text-zinc-500"
                    >
                        <ChevronLeft className="h-5 w-5"/>
                    </button>
                    <span className="text-xs text-zinc-300">Current Page: {currentPage} / {paginationInfo.totalPages}</span>
                    <button
                        disabled={currentPage == paginationInfo.totalPages}
                        onClick={() => setCurrentPage(prev => Math.min(paginationInfo.totalPages, prev + 1))}
                        className="text-zinc-300 hover:text-zinc-300 disabled:text-zinc-500"
                    >
                        <ChevronRight className="h-5 w-5"/>
                    </button>
                </div>
              )}
            </>
          </ul>
    )
}

export default AllProductsSearchList