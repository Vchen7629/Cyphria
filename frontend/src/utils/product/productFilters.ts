import { ProductV3 } from "../../mock/types";

/** 
    @function

    @description - Filter an array of products based on the filter tab (best, discussed, approval, hidden_gems)

    @param {string} activeFilter - the current filter that is active
    @param {ProductV3} productsList - the original array of products we are filtering on

    @returns {ProductV3[]} - the filtered array of products
*/
export function FilterByBadge(activeFilter: string, productsList: ProductV3[]) {
    switch (activeFilter) {
      case "best":
        return productsList.sort((a, b) => a.rank - b.rank);
      case "discussed":
        return productsList.sort((a, b) => b.mention_count - a.mention_count);
      case "approval":
        return productsList.sort((a, b) => b.approval_percentage - a.approval_percentage);
      case "hidden_gems":
        return productsList.filter((p) => p.is_hidden_gem || (p.approval_percentage > 75 && p.mention_count < 500));
      default:
        return productsList;
    }
}

/** 
    @function

    @description - Filter an array of products based on the search term matching the product name

    @param {string} searchTerm - the search term we are matching product names on
    @param {ProductV3} productsList - the original array of products we are filtering on

    @returns {ProductV3[]} - the filtered array of products
*/
export function FilterBySearchTerm(searchTerm: string, productsList: ProductV3[]) {
    if (!searchTerm.trim()) {
        return productsList;
    }

    const searchLower = searchTerm.toLowerCase();
    return productsList.filter((product) =>
        product.product_name.toLowerCase().includes(searchLower)
    );
} 