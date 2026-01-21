import type { ProductV3, Comment } from "../../mock/types";
import ProductRow from "./ProductRow";

interface ProductListProps {
  products: ProductV3[];
  comments?: Comment[];
  isLoading?: boolean;
}

const ProductList = ({ products, comments = [], isLoading = false }: ProductListProps) => {
  if (products.length === 0 && !isLoading) {
    return (
      <div className="py-12 text-center">
        <p className="text-zinc-500 text-sm">No products found</p>
      </div>
    );
  }

  return (
    <ul>
      {products.map((product) => (
        <ProductRow key={product.id} product={product} comments={comments} />
      ))}
    </ul>
  );
}

export default ProductList
